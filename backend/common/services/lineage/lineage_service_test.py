import logging
import pprint
import re
from itertools import groupby

import pytest
from beanie import PydanticObjectId
from jaro import jaro_winkler_metric

from backend.common.db.init import init_db
from backend.common.models.document import LineageCompare, RetrievedDocument, SiteRetrievedDocument
from backend.common.services.lineage.lineage_service import (
    LineageService,
    jaccard,
    tokenize_url,
    unique_by_attr,
)
from backend.scrapeworker.common.state_parser import (
    guess_state_abbr,
    guess_state_name,
    guess_year_part,
)

pp = pprint.PrettyPrinter(depth=4)


def get_reference_tags(tags):
    return [tag for tag in tags if not tag.focus]


def get_focus_tags(tags):
    return [tag for tag in tags if tag.focus]


def tokenize_filename(filename: str):
    return re.split("[^a-zA-Z0-9]", filename)


@pytest.mark.asyncio()
async def test_this():
    await init_db()

    lineage: LineageService = LineageService(log=logging)
    site_id = PydanticObjectId("6318a19a4ea2c09a1c61a14f")
    docs = await lineage.process_lineage_for_site(site_id)

    #  pull all docs for site grouped by doc_type, ordered by effective date
    results = []
    for doc in docs:
        lineage_compare = LineageCompare(
            doc_id=doc.id,
            site_id=doc.site_id,
            effective_date=doc.effective_date,
            document_type=doc.document_type,
        )

        lineage_compare.focus_therapy_tags = unique_by_attr(
            get_focus_tags(doc.therapy_tags), "code"
        )
        lineage_compare.ref_therapy_tags = unique_by_attr(
            get_reference_tags(doc.therapy_tags), "code"
        )

        lineage_compare.focus_indication_tags = unique_by_attr(
            get_focus_tags(doc.indication_tags), "code"
        )
        lineage_compare.ref_indication_tags = unique_by_attr(
            get_reference_tags(doc.indication_tags), "code"
        )

        [*path_parts, filename] = tokenize_url(doc.url)
        lineage_compare.pathname_tokens = path_parts
        lineage_compare.filename_tokens = tokenize_filename(filename)
        # await lineage_compare.save()
        results.append(lineage_compare)

    #  try by doc type... whats the fail indicator?

    results = sorted(results, key=lambda x: x.document_type)
    groups = groupby(results, lambda result: (result.document_type))
    for key, group in groups:

        # pick some kind of starting point .. doctype

        # easiest check, similar location context (fails outright somtimes)
        group_list = list(group)
        first_item = group_list.pop()
        possible_lineage_by_doc_type = [first_item.doc_id]

        for item in group_list:
            filename_match = jaccard(first_item.filename_tokens, item.filename_tokens)
            ref_indication_match = jaccard(first_item.ref_indication_tags, item.ref_indication_tags)
            # random numbers ...
            if filename_match >= 0.75 and ref_indication_match >= 0.75:
                possible_lineage_by_doc_type.append(item.doc_id)
            # print(filename_match)

        # i guess make lineage from group
        pp.pprint(possible_lineage_by_doc_type)
