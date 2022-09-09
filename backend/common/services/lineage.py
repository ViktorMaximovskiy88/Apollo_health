import pprint
from logging import Logger

from beanie import PydanticObjectId
from jarowinkler import jarowinkler_similarity

from backend.common.models.lineage import Lineage, LineageCompare
from backend.common.models.shared import get_unique_focus_tags, get_unique_reference_tags
from backend.common.models.site import Site
from backend.common.services.document import SiteRetrievedDocument, get_site_docs
from backend.scrapeworker.common.utils import (
    group_by_attr,
    jaccard,
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
            docs = await self.process_lineage_for_site(site.id)

        await self.process_lineage_for_docs(docs)

    async def process_lineage_for_site(self, site_id: PydanticObjectId):
        docs = await get_site_docs(site_id)
        await self.process_lineage_for_docs(docs)

    async def process_lineage_for_docs(self, docs: list[SiteRetrievedDocument]):
        compare_models = []
        # build the model, currently saving but mreh
        for doc in docs:
            lineage_compare = build_lineage_compare(doc)
            await lineage_compare.save()
            compare_models.append(lineage_compare)

        # run on groups (one way to pick similar is doc type; TODO put more thought into it )
        for _key, group in group_by_attr(docs, "document_type"):
            await self._process_lineage(list(group))

    async def _process_lineage(self, items):
        if len(items) == 0:
            return

        first_item: LineageCompare = items.pop()
        lineage = await Lineage(entries=[first_item.doc_id]).save()
        first_item.lineage_id = lineage.id
        unmatched = []

        item: LineageCompare
        for item in items:
            element_text_match = jarowinkler_similarity(first_item.element_text, item.element_text)
            filename_match = jaccard(first_item.filename_tokens, item.filename_tokens)
            ref_indication_match = jaccard(first_item.ref_indication_tags, item.ref_indication_tags)

            # TODO refactor this for varying rulesets (this one example...)
            if (
                filename_match >= 0.60 or element_text_match >= 0.90
            ) and ref_indication_match >= 0.85:
                self.log.info(item.filename, "MATCHED")
                lineage.entries.append(item.doc_id)
            else:
                self.log.info(item.filename, "UNMATCHED")
                unmatched.append(item)

        await first_item.save()
        await lineage.save()
        await self._process_lineage(unmatched)


def build_lineage_compare(doc: SiteRetrievedDocument) -> LineageCompare:
    lineage_compare = LineageCompare(
        doc_id=doc.id,
        site_id=doc.site_id,
        effective_date=doc.effective_date,
        document_type=doc.document_type,
        element_text=doc.link_text,
    )

    lineage_compare.focus_therapy_tags = get_unique_focus_tags(doc.therapy_tags)
    lineage_compare.ref_therapy_tags = get_unique_reference_tags(doc.therapy_tags)

    lineage_compare.focus_indication_tags = get_unique_focus_tags(doc.indication_tags)
    lineage_compare.ref_indication_tags = get_unique_reference_tags(doc.indication_tags)

    [*path_parts, filename] = tokenize_url(doc.url)
    lineage_compare.filename = filename
    lineage_compare.pathname_tokens = path_parts
    lineage_compare.filename_tokens = tokenize_filename(filename)

    return lineage_compare
