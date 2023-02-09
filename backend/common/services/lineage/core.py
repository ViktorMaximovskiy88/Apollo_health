import asyncio
import pprint
from logging import Logger

from beanie import PydanticObjectId

from backend.common.core.enums import ApprovalStatus
from backend.common.models.doc_document import DocDocument
from backend.common.models.document import RetrievedDocument
from backend.common.models.document_analysis import DocumentAnalysis, DocumentAnalysisLineage
from backend.common.models.site import Site
from backend.common.services.document import get_site_docs, get_site_docs_for_ids
from backend.common.services.lineage.model.model import LineageModel
from backend.common.services.tag_compare import TagCompare


class LineageService:
    def __init__(self, logger: Logger) -> None:
        self.logger = logger
        self.pp = pprint.PrettyPrinter(depth=4)
        self.tag_compare = TagCompare()
        self.model = LineageModel()

    async def get_comparision_docs(
        self, site_id: PydanticObjectId | None
    ) -> list[DocumentAnalysis]:
        query = DocumentAnalysis.find({"site_id": site_id})
        docs = await query.to_list()
        return docs

    async def clear_lineage_for_site(self, site_id: PydanticObjectId):
        self.logger.info(f"before clear_lineage_for_site {site_id}")
        await asyncio.gather(
            RetrievedDocument.get_motor_collection().update_many(
                {"locations.site_id": site_id},
                {
                    "$set": {
                        "lineage_id": None,
                        "is_current_version": False,
                        "previous_doc_id": None,
                    }
                },
            ),
            DocDocument.get_motor_collection().update_many(
                {"locations.site_id": site_id},
                {
                    "$set": {
                        "lineage_id": None,
                        "is_current_version": False,
                        "previous_doc_doc_id": None,
                    }
                },
            ),
            DocumentAnalysis.get_motor_collection().delete_many({"site_id": site_id}),
        )
        self.logger.info(f"after clear_lineage_for_site {site_id}")

    async def clear_all_lineage(self):
        await asyncio.gather(
            RetrievedDocument.get_motor_collection().update_many(
                {},
                {
                    "$set": {
                        "lineage_id": None,
                        "is_current_version": False,
                        "previous_doc_id": None,
                    }
                },
            ),
            DocDocument.get_motor_collection().update_many(
                {},
                {
                    "$set": {
                        "lineage_id": None,
                        "is_current_version": False,
                        "previous_doc_doc_id": None,
                    }
                },
            ),
            DocumentAnalysis.get_motor_collection().delete_many({}),
        )

    async def process_all_sites(self):
        site: Site
        async for site in Site.get_active_sites():
            await self.process_lineage_for_site(site.id)  # type: ignore

    async def process_lineage_for_site(self, site_id: PydanticObjectId, overwrite=False):
        docs: list[DocumentAnalysisLineage] = await get_site_docs(site_id)
        await self.process_lineage_for_docs(site_id, docs, overwrite)

    async def get_shared_lineage_sites(self, site_id: PydanticObjectId):
        docs = await DocDocument.find_many({"locations.site_id": site_id}).to_list()
        site_ids = set()
        for doc in docs:
            for location in doc.locations:
                site_ids.add(location.site_id)
        return list(site_ids)

    async def reprocess_lineage_for_site(self, site_id: PydanticObjectId):
        # we also want to clear for shared lineage sites
        site_ids = await self.get_shared_lineage_sites(site_id)
        self.logger.info(f"reprocess_lineage_for_site({site_id}) with site_ids={site_ids}")
        for site_id in site_ids:
            self.logger.info(f"clear/update for site {site_id}")
            await self.clear_lineage_for_site(site_id)
            # TODO reconcile the 'up-to-date' bits

        for site_id in site_ids:
            self.logger.info(f"reprocessing for site {site_id}")
            await self.process_lineage_for_site(site_id, True)

    async def process_lineage_for_doc_ids(
        self, site_id: PydanticObjectId, doc_ids: list[PydanticObjectId]
    ):
        docs: list[DocumentAnalysisLineage] = await get_site_docs_for_ids(site_id, doc_ids)
        await self.process_lineage_for_docs(site_id, docs)

    async def process_lineage_for_docs(
        self, site_id: PydanticObjectId, docs: list[DocumentAnalysisLineage], overwrite=False
    ):
        # pick all from DB that are most recent OR no lineage...
        compare_docs: list[DocumentAnalysis] = await self.get_comparision_docs(site_id)
        await self.process_lineage(compare_docs, docs, overwrite)

    async def apply_lineage_updates(self, lineage: list[DocumentAnalysis], overwrite=False):
        updates = []
        for analyses in lineage:
            updates.append(version_doc(analyses))
            updates.append(version_doc_doc(analyses, overwrite))
            updates.append(analyses.save())
        await asyncio.gather(*updates)

    def docs_to_preserve_lineage(self, docs: list[DocumentAnalysisLineage]):
        """Returns a set of document ids whose lineage should not be altered.
        This includes documents that are approved and have a lineage id
        or are a previous version of such a document.
        """
        preserved_doc_ids = set()
        docs_by_id = {d.doc_document_id: d for d in docs}
        docs_to_review = [
            d for d in docs if d.classification_status == ApprovalStatus.APPROVED and d.lineage_id
        ]
        while docs_to_review:
            doc = docs_to_review.pop()
            preserved_doc_ids.add(doc.doc_document_id)
            if doc.previous_doc_doc_id and doc.previous_doc_doc_id in docs_by_id:
                prev = docs_by_id[doc.previous_doc_doc_id]
                docs_to_review.append(prev)
        return preserved_doc_ids

    async def process_lineage(
        self, items: list[DocumentAnalysis], docs: list[DocumentAnalysisLineage], overwrite=False
    ):
        preserved_doc_ids = self.docs_to_preserve_lineage(docs)
        preserved_items = [item for item in items if item.doc_document_id in preserved_doc_ids]
        items_to_relineage = [
            item for item in items if item.doc_document_id not in preserved_doc_ids
        ]
        lineages = self.model.add_documents_to_lineages(items_to_relineage, preserved_items)
        for lineage in lineages:
            await self.apply_lineage_updates(lineage, overwrite)

    # TODO is this being called still (couldnt find it)?
    async def compare_tags(
        self, doc: RetrievedDocument, doc_doc: DocDocument, prev_doc_doc: DocDocument
    ) -> tuple[RetrievedDocument, DocDocument]:

        tag_lineage = await self.tag_compare.execute_and_save(doc_doc, prev_doc_doc)
        self.logger.info(f"'after compare tags {doc_doc.id}")
        # TODO will be removed with rtdoc banishment
        doc.therapy_tags = tag_lineage.therapy_tags
        doc.indication_tags = tag_lineage.indication_tags
        doc = await doc.save()
        return doc, doc_doc


async def version_doc(doc_analysis: DocumentAnalysis):
    doc = await RetrievedDocument.get(doc_analysis.retrieved_document_id)
    if not doc:
        raise Exception(f"RetrievedDocument {doc_analysis.retrieved_document_id} does not exist")

    doc.lineage_id = doc_analysis.lineage_id
    doc.is_current_version = doc_analysis.is_current_version
    doc.lineage_confidence = doc_analysis.confidence
    doc.previous_doc_id = doc_analysis.previous_doc_doc_id
    doc = await doc.save()
    return doc


async def inherit_prev_doc_fields(doc: DocDocument, site_id: PydanticObjectId):
    if not doc.previous_doc_doc_id:  # Nothing to inherit
        return

    prev_doc = await DocDocument.get(doc.previous_doc_doc_id)
    if not prev_doc:
        return

    if prev_doc.translation_id:
        doc.translation_id = prev_doc.translation_id

    if prev_doc.internal_document:
        doc.internal_document = prev_doc.internal_document

    if prev_doc.document_family_id:
        doc.document_family_id = prev_doc.document_family_id

    loc = next(loc for loc in doc.locations if site_id == loc.site_id)
    prev_loc = next((loc for loc in prev_doc.locations if site_id == loc.site_id), None)

    if prev_loc and prev_loc.payer_family_id:
        loc.payer_family_id = prev_loc.payer_family_id


async def version_doc_doc(doc_analysis: DocumentAnalysis, overwrite=False):
    doc = await DocDocument.get(doc_analysis.doc_document_id)  # type: ignore
    if not doc:
        raise Exception(f"DocDocument {doc_analysis.doc_document_id} does not exists")

    # Don't modify DocDocument Lineage if Lineage is Already Approved
    if not overwrite and doc.classification_status == ApprovalStatus.APPROVED and doc.lineage_id:
        return doc

    doc.lineage_id = doc_analysis.lineage_id
    doc.is_current_version = doc_analysis.is_current_version
    doc.lineage_confidence = doc_analysis.confidence
    doc.previous_doc_doc_id = doc_analysis.previous_doc_doc_id

    await inherit_prev_doc_fields(doc, doc_analysis.site_id)
    doc = await doc.save()
    return doc
