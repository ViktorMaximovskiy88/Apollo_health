import asyncio
import pprint
from logging import Logger

from beanie import PydanticObjectId

from backend.app.scripts.retag_document import ReTagger
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
from backend.common.services.lineage_matcher import LineageMatcher
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

    async def clear_lineage_for_site(self, site_id: PydanticObjectId | None):
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

    async def update_site_docs(self, site_id):
        # Updates tags, doc vecs and whatever else we need for lineage
        # using retagger for now
        retagger = ReTagger()
        await retagger.indication.model()
        site = await Site.get(site_id)
        await retagger.retag_docs_on_site(site, 0)

    async def process_all_sites(self):
        async for site in Site.find():
            await self.process_lineage_for_site(site.id)

    async def process_lineage_for_site(self, site_id: PydanticObjectId):
        docs = await get_site_docs(site_id)
        await self.process_lineage_for_docs(site_id, docs)

    async def reprocess_lineage_for_site(self, site_id: PydanticObjectId):
        await self.update_site_docs(site_id)
        await self.clear_lineage_for_site(site_id)
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
        for doc in docs:
            await build_doc_analysis(doc)

        # pick all from DB that are most recent OR no lineage...
        compare_docs = await self.get_comparision_docs(site_id)
        # TODO prob shouldnt group docs that are already lineage'd?
        for _key, group in group_by_attr(compare_docs, "document_type"):
            await self._process_lineage(list(group))

    async def _process_lineage(self, items: list[DocumentAnalysis]):
        if len(items) == 0:
            self.logger.info("no items remain")
            return

        missing_lineage = [item for item in items if not item.lineage_id]
        if len(missing_lineage) == 0:
            self.logger.info("all lineage assigned")
            return

        matched = []
        unmatched = []
        item: DocumentAnalysis

        first_item: DocumentAnalysis = missing_lineage.pop()
        first_item = await create_lineage(first_item)
        matched.append(first_item)

        for item in items:
            match = LineageMatcher(first_item, item, logger=self.logger).exec()
            if match:
                self.logger.info(f"MATCHED {first_item.filename_text} {item.filename_text}")

                if item.lineage_id:
                    first_item.lineage_id = item.lineage_id
                else:
                    item.lineage_id = first_item.lineage_id

                await asyncio.gather(first_item.save(), item.save())
                matched.append(item)

            else:
                self.logger.info(f"UNMATCHED {first_item.filename_text} {item.filename_text}")
                unmatched.append(item)

        # Theoretically unmatched shouldnt be matched with previous, so lets assign prev doc here
        # TODO what if we dont have effective date ... last collected :x
        await self._version_matched(matched)
        await self._process_lineage(unmatched)

    def sort_matched(self, items: list[DocumentAnalysis]):
        items.sort(key=lambda x: x.final_effective_date or x.year_part or 0)
        return items

    async def _version_matched(self, items: list[DocumentAnalysis]):
        matches = self.sort_matched(items)
        print(matches)
        prev_doc = None
        prev_doc_doc = None
        for index, match in enumerate(matches):
            is_last = index == len(matches) - 1
            doc, doc_doc = await asyncio.gather(
                version_doc(match, is_last, prev_doc),
                version_doc_doc(match, is_last, prev_doc_doc),
            )
            prev_doc = doc
            prev_doc_doc = doc_doc


async def create_lineage(item: DocumentAnalysis):
    lineage_id = PydanticObjectId()
    item.lineage_id = lineage_id
    item = await item.save()
    return item


async def version_doc(doc_analysis: DocumentAnalysis, is_last: bool, prev_doc: RetrievedDocument):
    doc = await RetrievedDocument.get(doc_analysis.retrieved_document_id)
    doc.lineage_id = doc_analysis.lineage_id
    doc.is_current_version = is_last
    doc.previous_doc_id = prev_doc.id if prev_doc else None
    doc = await doc.save()
    return doc


async def version_doc_doc(doc_analysis: DocumentAnalysis, is_last: bool, prev_doc: DocDocument):
    doc = await DocDocument.find_one({"retrieved_document_id": doc_analysis.retrieved_document_id})
    doc.lineage_id = doc_analysis.lineage_id
    doc.is_current_version = is_last
    doc.previous_doc_doc_id = prev_doc.id if prev_doc else None
    doc = await doc.save()
    return doc


def build_attr_model(input: str) -> DocumentAttrs:
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

    doc_analysis = await DocumentAnalysis.find_one({"retrieved_document_id": doc.id})

    if not doc_analysis:
        doc_analysis = DocumentAnalysis(
            retrieved_document_id=doc.id,
            name=doc.name,
            site_id=doc.site_id,
            final_effective_date=calc_final_effective_date(doc),
            document_type=doc.document_type,
            element_text=doc.link_text,
            file_size=doc.file_size,
            doc_vectors=doc.doc_vectors,
        )

    doc_analysis.focus_therapy_tags = get_unique_focus_tags(doc.therapy_tags)
    doc_analysis.ref_therapy_tags = get_unique_reference_tags(doc.therapy_tags)

    doc_analysis.focus_indication_tags = get_unique_focus_tags(doc.indication_tags)
    doc_analysis.ref_indication_tags = get_unique_reference_tags(doc.indication_tags)

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
    doc_analysis.year_part = consensus_attr(doc_analysis, "year_part")

    doc_analysis = await doc_analysis.save()

    return doc_analysis
