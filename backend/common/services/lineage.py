import asyncio
import pprint
from logging import Logger

from beanie import PydanticObjectId

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
    def __init__(self, log: Logger) -> None:
        self.log = log
        self.pp = pprint.PrettyPrinter(depth=4)

    async def process_lineage_for_sites(self):
        sites = await Site.find().to_list()
        for site in sites:
            await self.process_lineage_for_site(site.id)

    async def process_lineage_for_site(self, site_id: PydanticObjectId):
        docs = await get_site_docs(site_id)
        await self.process_lineage_for_docs(docs)

    async def process_lineage_for_doc_ids(
        self, site_id: PydanticObjectId, doc_ids: list[PydanticObjectId]
    ):
        docs = await get_site_docs_for_ids(site_id, doc_ids)
        await self.process_lineage_for_docs(docs)

    async def process_lineage_for_docs(self, docs: list[SiteRetrievedDocument]):
        compare_models = []
        # build the model, currently saving it too
        for doc in docs:
            doc_analysis = build_doc_analysis(doc)
            await doc_analysis.save()

            similar_docs = await DocumentAnalysis.find(
                {
                    "_id": {"$ne": doc_analysis.id},
                    "lineage_id": None,
                    "document_type": doc_analysis.document_type,
                    "site_id": doc_analysis.site_id,
                }
            ).to_list()

            compare_models.append(doc_analysis)
            print(len(compare_models), "compare_models before")
            compare_models += similar_docs
            print(len(compare_models), "compare_models after")

        # run on groups (one way to pick similar is doc type; TODO put more thought into it )
        for _key, group in group_by_attr(compare_models, "document_type"):
            await self._process_lineage(list(group))

    async def _process_lineage(self, items: list[DocumentAnalysis]):
        if len(items) == 0:
            return

        missing_lineage = [item for item in items if not item.lineage_id]
        if len(missing_lineage) == 0:
            return

        first_item: DocumentAnalysis = items.pop()

        unmatched = []
        item: DocumentAnalysis
        for item in items:
            match = LineageMatcher(first_item, item).exec()
            if match:
                self.log.info(f"MATCHED {item.filename}")

                if item.lineage_id:
                    first_item.lineage_id = item.lineage_id
                else:
                    lineage_id = PydanticObjectId()
                    first_item.lineage_id = lineage_id
                    item.lineage_id = lineage_id

                await asyncio.gather(
                    first_item.save(),
                    item.save(),
                )

            else:
                self.log.info(f"UNMATCHED {item.filename}")
                unmatched.append(item)

        await self._process_lineage(unmatched)


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


def build_doc_analysis(doc: SiteRetrievedDocument) -> DocumentAnalysis:
    doc_analysis = DocumentAnalysis(
        retrieved_document_id=doc.id,
        site_id=doc.site_id,
        effective_date=doc.effective_date,
        document_type=doc.document_type,
        element_text=doc.link_text,
        file_size=doc.file_size,
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

    return doc_analysis
