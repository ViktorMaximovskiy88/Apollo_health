import logging
import pprint

import pytest
from beanie import PydanticObjectId

from backend.common.db.init import init_db
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


@pytest.mark.asyncio()
async def test_this():
    await init_db()

    lineage: LineageService = LineageService(log=logging)
    site_id = PydanticObjectId("6318a19a4ea2c09a1c61a14f")
    docs = await lineage.process_lineage_for_site(site_id)

    results = []
    for index, doc in enumerate(docs):
        location = doc.get_site_location(site_id)

        tags_a = unique_by_attr(doc.indication_tags, "code")
        similiar = 0
        if index + 1 < len(docs):
            tags_b = unique_by_attr(docs[index + 1].indication_tags, "code")
            similiar = jaccard(tags_a, tags_b)

        [*path_parts, filename] = tokenize_url(location.url)
        path = "/".join(path_parts)

        print(filename, similiar)
        result = {
            "pathname": {
                "year_part": guess_year_part(path),
                "state_name": guess_state_name(location.link_text),
                "state_abbr": guess_state_abbr(path),
            },
            "filename": {
                "state_abbr": guess_state_abbr(filename),
                "state_name": guess_state_name(location.link_text),
                "year_part": guess_year_part(filename),
            },
            "element": {
                "state_abbr": guess_state_abbr(location.link_text),
                "state_name": guess_state_name(location.link_text),
                "year_part": guess_year_part(location.link_text),
            },
            "parent": {
                "state_abbr": guess_state_abbr(location.closest_heading),
                "state_name": guess_state_name(location.closest_heading),
                "year_part": guess_year_part(location.closest_heading),
            },
        }
        results.append(result)

    pp.pprint(results)
