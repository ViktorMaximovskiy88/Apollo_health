import asyncio
import pprint
from logging import Logger

from beanie import PydanticObjectId

from backend.app.scripts.retag_document import ReTagger
from backend.common.core.enums import ApprovalStatus
from backend.common.models.doc_document import DocDocument
from backend.common.models.document import RetrievedDocument
from backend.common.models.document_mixins import calc_final_effective_date
from backend.common.models.lineage import DocumentAnalysis, DocumentAttrs
from backend.common.models.shared import get_unique_focus_tags, get_unique_reference_tags
from backend.common.models.site import Site
from backend.common.services.document import (
    SiteRetrievedDocument,
    get_site_docs,
    get_site_docs_for_ids,
)
from backend.common.services.lineage.lineage_matcher import LineageMatcher
from backend.common.services.tag_compare import TagCompare
from backend.scrapeworker.common.lineage_parser import (
    guess_month_abbr,
    guess_month_name,
    guess_month_part,
    guess_state_abbr,
    guess_state_name,
    guess_year_part,
)
from backend.scrapeworker.common.utils import (
    compact,
    group_by_attr,
    tokenize_filename,
    tokenize_url,
)


class LineageService:
    def __init__(self, logger: Logger) -> None:
        self.logger = logger
        self.pp = pprint.PrettyPrinter(depth=4)
        self.tag_compare = TagCompare()

    async def get_comparision_docs(
        self, site_id: PydanticObjectId | None
    ) -> list[DocumentAnalysis]:
        query = DocumentAnalysis.find(
            {
                "$or": [
                    {"lineage_id": None},
                    {"is_current_version": True},
                ],
            }
        )

        if site_id:
            DocumentAnalysis.find({"site_id": site_id})

        docs = await query.to_list()
        return docs

    async def clear_lineage_for_site(self, site_id: PydanticObjectId):
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

    async def update_site_docs(self, site_id):
        # Updates tags, doc vecs and whatever else we need for lineage
        # using retagger for now
        retagger = ReTagger()
        await retagger.indication.model()
        site = await Site.get(site_id)
        if not site:
            raise Exception(f"Site Id {site_id} does not exists")
        await retagger.retag_docs_on_site(site, 0)

    async def process_all_sites(self):
        async for site in Site.find():
            await self.process_lineage_for_site(site.id)  # type: ignore

    async def process_lineage_for_site(self, site_id: PydanticObjectId):
        docs = await get_site_docs(site_id)
        await self.process_lineage_for_docs(site_id, docs)

    async def get_shared_lineage_sites(self, site_id: PydanticObjectId):
        docs = await RetrievedDocument.find_many({"locations.site_id": site_id}).to_list()
        site_ids = set()
        for doc in docs:
            for location in doc.locations:
                site_ids.add(location.site_id)
        return list(site_ids)

    async def reprocess_lineage_for_site(self, site_id: PydanticObjectId):
        # we also want to clear for shared lineage sites
        site_ids = await self.get_shared_lineage_sites(site_id)

        for site_id in site_ids:
            self.logger.info(f"clear/update for site {site_id}")
            await self.clear_lineage_for_site(site_id)
            await self.update_site_docs(site_id)

        for site_id in site_ids:
            self.logger.info(f"reprocessing for site {site_id}")
            await self.process_lineage_for_site(site_id)

    async def process_lineage_for_doc_ids(
        self, site_id: PydanticObjectId, doc_ids: list[PydanticObjectId]
    ):
        docs = await get_site_docs_for_ids(site_id, doc_ids)
        await self.process_lineage_for_docs(site_id, docs)

    async def process_lineage_for_docs(
        self, site_id: PydanticObjectId, docs: list[SiteRetrievedDocument]
    ):
        # build the model and save it
        self.logger.info(f"before doc analysis save len(docs)={len(docs)}")
        for doc in docs:
            await build_doc_analysis(doc)
        self.logger.info(f"after doc analysis save len(docs)={len(docs)}")

        # pick all from DB that are most recent OR no lineage...
        compare_docs = await self.get_comparision_docs(site_id)
        await self.process_lineage(compare_docs)

    async def process_lineage(self, items: list[DocumentAnalysis]):

        pending_items = [item for item in items if not item.lineage_id]
        lineaged_items = [item for item in items if item.lineage_id]

        self.logger.info(f"pending_items={len(pending_items)} lineaged_items={len(lineaged_items)}")

        while len(pending_items) > 0:
            pending_item: DocumentAnalysis = pending_items.pop()

            matched_item = None
            for lineaged_item in lineaged_items:
                match = LineageMatcher(pending_item, lineaged_item, logger=self.logger).exec()
                if match:
                    matched_item = lineaged_item
                    break

            if matched_item:
                self.logger.debug(f"'{pending_item.filename}' '{matched_item.filename}' -> MATCHED")
                pending_item.lineage_id = matched_item.lineage_id
                await pending_item.save()
                lineaged_items.append(pending_item)
            else:
                self.logger.debug(f"'{pending_item.filename_text}' -> UNMATCHED")
                pending_item = await create_lineage(pending_item)
                lineaged_items.append(pending_item)

        await self._version_matched(lineaged_items)

    def sort_matched(self, items: list[DocumentAnalysis]):
        items.sort(key=lambda x: x.final_effective_date or x.year_part or 0)
        return items

    async def compare_tags(
        self, doc: RetrievedDocument, doc_doc: DocDocument, prev_doc: RetrievedDocument
    ) -> tuple[RetrievedDocument, DocDocument]:
        ther_tags, indi_tags = self.tag_compare.execute(doc, prev_doc)
        doc.therapy_tags = ther_tags
        doc.indication_tags = indi_tags
        doc_doc.therapy_tags = ther_tags
        doc_doc.indication_tags = indi_tags
        doc, doc_doc = await asyncio.gather(doc.save(), doc_doc.save())
        return doc, doc_doc

    async def _version_matched(self, items: list[DocumentAnalysis]):
        for _key, group in group_by_attr(items, "lineage_id"):
            matches = self.sort_matched(list(group))
            prev_doc = None
            prev_doc_doc = None
            for index, match in enumerate(matches):
                is_last = index == len(matches) - 1
                doc, doc_doc = await asyncio.gather(
                    version_doc(match, is_last, prev_doc),
                    version_doc_doc(match, is_last, prev_doc_doc),
                )
                if is_last and prev_doc:
                    doc, doc_doc = await self.compare_tags(doc, doc_doc, prev_doc)
                prev_doc = doc
                prev_doc_doc = doc_doc


async def create_lineage(item: DocumentAnalysis):
    lineage_id = PydanticObjectId()
    item.lineage_id = lineage_id
    item = await item.save()
    return item


async def version_doc(
    doc_analysis: DocumentAnalysis, is_last: bool, prev_doc: RetrievedDocument | None
):
    doc = await RetrievedDocument.get(doc_analysis.retrieved_document_id)
    if not doc:
        raise Exception(f"RetrievedDocument {doc_analysis.retrieved_document_id} does not exist")

    doc.lineage_id = doc_analysis.lineage_id
    doc.is_current_version = is_last
    doc.previous_doc_id = prev_doc.id if prev_doc else None
    doc = await doc.save()
    return doc


def inherit_prev_doc_fields(
    doc: DocDocument, prev_doc: DocDocument | None, site_id: PydanticObjectId
):
    if not prev_doc:  # Nothing to inherit
        return

    if prev_doc.translation_id:
        doc.translation_id = prev_doc.translation_id

    if prev_doc.internal_document:
        doc.internal_document = prev_doc.internal_document

    if prev_doc.document_family_id:
        doc.document_family_id = prev_doc.document_family_id

    loc = next(loc for loc in doc.locations if site_id == loc.site_id)
    prev_loc = next(loc for loc in prev_doc.locations if site_id == loc.site_id)

    if prev_loc.payer_family_id:
        loc.payer_family_id = prev_loc.payer_family_id


async def version_doc_doc(
    doc_analysis: DocumentAnalysis, is_last: bool, prev_doc: DocDocument | None
):
    doc = await DocDocument.find_one({"retrieved_document_id": doc_analysis.retrieved_document_id})
    if not doc:
        raise Exception(f"DocDocument {doc_analysis.retrieved_document_id} does not exists")

    # Don't modify DocDocument Lineage if Lineage is Already Approved
    if doc.classification_status == ApprovalStatus.APPROVED and doc.lineage_id:
        return doc

    doc.lineage_id = doc_analysis.lineage_id
    doc.is_current_version = is_last
    doc.previous_doc_doc_id = prev_doc.id if prev_doc else None
    inherit_prev_doc_fields(doc, prev_doc, doc_analysis.site_id)
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


async def build_doc_analysis(doc: SiteRetrievedDocument) -> DocumentAnalysis:

    doc_analysis = await DocumentAnalysis.find_one(
        {"retrieved_document_id": doc.id, "site_id": doc.site_id}
    )

    if doc_analysis is None:
        doc_analysis = DocumentAnalysis(
            retrieved_document_id=doc.id,
            site_id=doc.site_id,
        )

    doc_analysis.name = doc.name
    doc_analysis.final_effective_date = calc_final_effective_date(doc)
    doc_analysis.document_type = doc.document_type
    doc_analysis.element_text = doc.link_text
    doc_analysis.file_size = doc.file_size
    doc_analysis.doc_vectors = doc.doc_vectors

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

    doc_analysis = await doc_analysis.save()

    return doc_analysis
