import asyncio
import pprint
from logging import Logger

from beanie import BulkWriter, PydanticObjectId

from backend.common.core.enums import ApprovalStatus
from backend.common.models.doc_document import DocDocument, SiteDocDocument
from backend.common.models.document import RetrievedDocument
from backend.common.models.document_mixins import calc_final_effective_date
from backend.common.models.lineage import DocumentAnalysis, DocumentAttrs
from backend.common.models.shared import get_unique_focus_tags, get_unique_reference_tags
from backend.common.models.site import Site
from backend.common.services.document import get_site_docs, get_site_docs_for_ids
from backend.common.services.lineage.model.model import LineageModel
from backend.common.services.tag_compare import TagCompare
from backend.scrapeworker.common.lineage_parser import (
    guess_month_abbr,
    guess_month_name,
    guess_month_part,
    guess_state_abbr,
    guess_state_name,
    guess_year_part,
)
from backend.scrapeworker.common.utils import compact, tokenize_filename, tokenize_url


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
        async for site in Site.find():
            await self.process_lineage_for_site(site.id)  # type: ignore

    async def process_lineage_for_site(self, site_id: PydanticObjectId, overwrite=False):
        docs = await get_site_docs(site_id)
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
        docs = await get_site_docs_for_ids(site_id, doc_ids)
        await self.process_lineage_for_docs(site_id, docs)

    async def refresh_doc_analyses(self, site_id: PydanticObjectId, docs: list[SiteDocDocument]):
        existing_analyses_query = DocumentAnalysis.find(
            {"doc_document_id": {"$in": [doc.id for doc in docs]}, "site_id": site_id}
        )
        doc_analyses: dict[PydanticObjectId, DocumentAnalysis] = {}
        async for analysis in existing_analyses_query:
            doc_analyses[analysis.doc_document_id] = analysis

        async with BulkWriter() as bulk_writer:
            for doc in docs:
                existing_analysis = doc_analyses.get(doc.id)
                doc_analysis = build_doc_analysis(doc, existing_analysis)
                if existing_analysis:
                    await DocumentAnalysis.replace(doc_analysis, bulk_writer=bulk_writer)
                else:
                    await DocumentAnalysis.insert_one(doc_analysis, bulk_writer=bulk_writer)

    async def process_lineage_for_docs(
        self, site_id: PydanticObjectId, docs: list[SiteDocDocument], overwrite=False
    ):
        # build the model and save it
        self.logger.info(f"site {site_id} before doc analysis save len(docs)={len(docs)}")
        await self.refresh_doc_analyses(site_id, docs)
        self.logger.info(f"site {site_id} after doc analysis save len(docs)={len(docs)}")

        # pick all from DB that are most recent OR no lineage...
        compare_docs = await self.get_comparision_docs(site_id)
        await self.process_lineage(compare_docs, docs, overwrite)

    async def apply_lineage_updates(self, lineage: list[DocumentAnalysis], overwrite=False):
        updates = []
        for analyses in lineage:
            updates.append(version_doc(analyses))
            updates.append(version_doc_doc(analyses, overwrite))
            updates.append(analyses.save())
        await asyncio.gather(*updates)

    def docs_to_preserve_lineage(self, docs: list[SiteDocDocument]):
        """Returns a set of document ids whose lineage should not be altered.
        This includes documents that are approved and have a lineage id
        or are a previous version of such a document.
        """
        preserved_doc_ids = set()
        docs_by_id = {d.id: d for d in docs}
        docs_to_review = [
            d for d in docs if d.classification_status == ApprovalStatus.APPROVED and d.lineage_id
        ]
        while docs_to_review:
            doc = docs_to_review.pop()
            preserved_doc_ids.add(doc.id)
            if doc.previous_doc_doc_id and doc.previous_doc_doc_id in docs_by_id:
                prev = docs_by_id[doc.previous_doc_doc_id]
                docs_to_review.append(prev)
        return preserved_doc_ids

    async def process_lineage(
        self, items: list[DocumentAnalysis], docs: list[SiteDocDocument], overwrite=False
    ):
        preserved_doc_ids = self.docs_to_preserve_lineage(docs)
        preserved_items = [item for item in items if item.doc_document_id in preserved_doc_ids]
        items_to_relineage = [
            item for item in items if item.doc_document_id not in preserved_doc_ids
        ]
        lineages = self.model.add_documents_to_lineages(items_to_relineage, preserved_items)
        for lineage in lineages:
            await self.apply_lineage_updates(lineage, overwrite)

    async def compare_tags(
        self, doc: RetrievedDocument, doc_doc: DocDocument, prev_doc_doc: DocDocument
    ) -> tuple[RetrievedDocument, DocDocument]:

        therapy_tags, indication_tags = await self.tag_compare.execute(doc_doc, prev_doc_doc)
        self.logger.info(f"'after compare tags {doc_doc.id}")
        # TODO will be removed with rtdoc banishment
        doc.therapy_tags = therapy_tags
        doc.indication_tags = indication_tags
        # NOTE the result here are TagUpdate Status changes,  _not_ new tags...
        doc_doc.therapy_tags = therapy_tags
        doc_doc.indication_tags = indication_tags
        doc, doc_doc = await asyncio.gather(doc.save(), doc_doc.save())
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
    doc = await DocDocument.get(doc_analysis.doc_document_id)
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


def build_attr_model(input: str | None) -> DocumentAttrs:
    return DocumentAttrs(
        state_abbr=guess_state_abbr(input),
        state_name=guess_state_name(input),
        year_part=guess_year_part(input),
        month_abbr=guess_month_abbr(input),
        month_name=guess_month_name(input),
        month_part=guess_month_part(input),
    )


# TODO tweak logic, for now its all or nothing
#  url, context, document
def consensus_attr(model: DocumentAnalysis, attr: str):
    all_attrs = compact(
        [
            getattr(model.filename, attr),
            getattr(model.pathname, attr),
            # TODO file and path are easier to guess due to human formatting of paths/urls/files
            getattr(model.element, attr),
            getattr(model.parent, attr),
            getattr(model.siblings, attr),
        ]
    )
    consensus = list(set(all_attrs))
    return consensus[0] if len(consensus) == 1 else None


def build_doc_analysis(
    doc: SiteDocDocument, doc_analysis: DocumentAnalysis | None
) -> DocumentAnalysis:
    if doc_analysis is None:
        doc_analysis = DocumentAnalysis(
            doc_document_id=doc.id,
            retrieved_document_id=doc.retrieved_document_id,
            previous_doc_doc_id=doc.previous_doc_doc_id,
            lineage_id=doc.lineage_id,
            confidence=doc.lineage_confidence,
            site_id=doc.site_id,
        )

    doc_analysis.file_size = doc.file_size
    doc_analysis.doc_vectors = doc.doc_vectors
    doc_analysis.token_count = doc.token_count

    doc_analysis.name = doc.name
    doc_analysis.final_effective_date = calc_final_effective_date(doc)
    doc_analysis.document_type = doc.document_type
    doc_analysis.element_text = doc.link_text

    doc_analysis.focus_therapy_tags = get_unique_focus_tags(doc.therapy_tags)
    doc_analysis.focus_indication_tags = get_unique_focus_tags(doc.indication_tags)
    doc_analysis.ref_therapy_tags = get_unique_reference_tags(doc.therapy_tags)
    doc_analysis.ref_indication_tags = get_unique_reference_tags(doc.indication_tags)

    doc_analysis.url_focus_therapy_tags = get_unique_focus_tags(doc.url_therapy_tags)
    doc_analysis.url_focus_indication_tags = get_unique_focus_tags(doc.url_indication_tags)

    doc_analysis.link_focus_therapy_tags = get_unique_focus_tags(doc.link_therapy_tags)
    doc_analysis.link_focus_indication_tags = get_unique_focus_tags(doc.link_indication_tags)

    [*path_parts, filename] = tokenize_url(doc.url)
    doc_analysis.filename_text = filename
    doc_analysis.pathname_text = "/".join(path_parts)
    doc_analysis.pathname_tokens = compact(path_parts)
    doc_analysis.filename_tokens = tokenize_filename(filename)

    doc_analysis.pathname = build_attr_model(doc_analysis.pathname_text)
    doc_analysis.filename = build_attr_model(doc_analysis.filename_text)
    doc_analysis.element = build_attr_model(doc_analysis.element_text)
    doc_analysis.parent = build_attr_model(doc_analysis.parent_text)
    doc_analysis.siblings = build_attr_model(doc_analysis.siblings_text)

    doc_analysis.state_abbr = consensus_attr(doc_analysis, "state_abbr")
    doc_analysis.state_name = consensus_attr(doc_analysis, "state_name")
    doc_analysis.month_abbr = consensus_attr(doc_analysis, "month_abbr")
    doc_analysis.month_name = consensus_attr(doc_analysis, "month_name")
    doc_analysis.year_part = (
        int(year_part) if (year_part := consensus_attr(doc_analysis, "year_part")) else 0
    )

    return doc_analysis
