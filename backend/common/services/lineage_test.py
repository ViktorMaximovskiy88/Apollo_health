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
from backend.common.services.lineage.lineage_service import (
    LineageService,
    jaccard,
    tokenize_url,
    unique_by_attr,
    get_site_docs,
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


def tokenize_string(input: str):
    return re.split("\s", input)


@pytest.mark.asyncio()
async def test_this():
    await init_db()

    sites = await Site.find().to_list()

    for site in sites:

        docs = await get_site_docs(site.id)

        #  pull all docs for site grouped by doc_type, ordered by effective date
        results = []
        for doc in docs:
            lineage_compare = LineageCompare(
                doc_id=doc.id,
                site_id=doc.site_id,
                effective_date=doc.effective_date,
                document_type=doc.document_type,
                element_text=doc.link_text,
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
            lineage_compare.filename = filename
            lineage_compare.pathname_tokens = path_parts
            lineage_compare.filename_tokens = tokenize_filename(filename)
            lineage_compare.element_text_tokens = tokenize_string(doc.link_text)
            lineage_compare.sibling_text_tokens = tokenize_string(
                doc.context_metadata.siblings_text.strip()
            )
            await lineage_compare.save()
            results.append(lineage_compare)

        #  try by doc type... whats the fail indicator?

        results = sorted(results, key=lambda x: x.document_type)
        groups = groupby(results, lambda result: (result.document_type))
        for key, group in groups:

            # pick some kind of starting point .. doctype
            await process_lineage(list(group))


async def process_lineage(items):
    if len(items) == 0:
        return

    first_item: LineageCompare = items.pop()
    lineage = await Lineage(entries=[first_item.doc_id]).save()
    first_item.lineage_id = lineage.id
    unmatched = []

    print(first_item.filename, " * * * * ")
    item: LineageCompare
    for item in items:
        element_text_match = jarowinkler_similarity(first_item.element_text, item.element_text)
        filename_match = jaccard(first_item.filename_tokens, item.filename_tokens)
        ref_indication_match = jaccard(first_item.ref_indication_tags, item.ref_indication_tags)
        print(
            jarowinkler_similarity(first_item.element_text, item.element_text),
            first_item.element_text,
            item.element_text,
        )
        print("score", filename_match, ref_indication_match, element_text_match)
        if (filename_match >= 0.60 or element_text_match >= 0.90) and ref_indication_match >= 0.85:
            print(item.filename, "MATCHED")
            lineage.entries.append(item.doc_id)
        else:
            print(item.filename, "UNMATCHED")
            unmatched.append(item)

    await first_item.save()
    await lineage.save()
    await process_lineage(unmatched)
