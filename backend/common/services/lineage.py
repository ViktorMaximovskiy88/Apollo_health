from logging import Logger as PyLogger

from beanie import PydanticObjectId

from backend.common.models.document import LineageCompare, SiteRetrievedDocument
from backend.scrapeworker.common.state_parser import guess_state_abbr
from backend.scrapeworker.common.utils import date_rgxs, label_rgxs


import logging
import pprint
import re
from itertools import groupby

import pytest
from beanie import PydanticObjectId
from jarowinkler import jarowinkler_similarity

from backend.common.db.init import init_db
from backend.common.models.site import Site
from backend.common.models.document import (
    Lineage,
    LineageCompare,
    RetrievedDocument,
    SiteRetrievedDocument,
)

from backend.scrapeworker.common.state_parser import (
    guess_state_abbr,
    guess_state_name,
    guess_year_part,
)

from backend.common.services.document import get_site_docs

pp = pprint.PrettyPrinter(depth=4)


class LineageService:
    def __init__(self, log: PyLogger) -> None:
        self.log = log

    async def process_lineage_for_site(self, site_id: PydanticObjectId):
        docs = await get_site_docs(site_id)
        result = await self.process_lineage_for_docs(docs)
        return result

    async def process_lineage_for_sites(self):
        sites = await Site.find().to_list()

        for site in sites:
            docs = await self.process_lineage_for_site(site.id)

        result = await self.process_lineage_for_docs(docs)
        return result

    async def process_lineage_for_docs(self, docs: list[SiteRetrievedDocument]):
        sites = await Site.find().to_list()

        for site in sites:

            docs = await get_site_docs(site.id)

    async def _process_lineage(self, items):
        if len(items) == 0:
            return

        first_item: LineageCompare = items.pop()
        lineage = await Lineage(entries=[first_item.doc_id]).save()
        first_item.lineage_id = lineage.id
        unmatched = []

        self.log.debug(first_item.filename, " * * * * ")
        item: LineageCompare
        for item in items:
            element_text_match = jarowinkler_similarity(first_item.element_text, item.element_text)
            filename_match = jaccard(first_item.filename_tokens, item.filename_tokens)
            ref_indication_match = jaccard(first_item.ref_indication_tags, item.ref_indication_tags)
            self.log.info(
                jarowinkler_similarity(first_item.element_text, item.element_text),
                first_item.element_text,
                item.element_text,
            )
            self.log.info("score", filename_match, ref_indication_match, element_text_match)
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
