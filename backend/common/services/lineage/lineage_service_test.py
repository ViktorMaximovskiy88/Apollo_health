import logging
import pprint

import pytest
from beanie import PydanticObjectId

from backend.common.db.init import init_db
from backend.common.services.lineage.lineage_service import LineageService, tokenize_url
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
    for doc in docs:
        location = doc.get_site_location(site_id)

        [*path_parts, filename] = tokenize_url(location.url)
        print(path_parts, filename)
        result = {
            "pathname": {
                "year_part": list(
                    set(
                        [
                            guess_year_part(part)
                            for part in path_parts
                            if guess_year_part(part) is not None
                        ]
                    )
                ),
                "state_abbr": list(
                    set(
                        [
                            guess_state_abbr(part)
                            for part in path_parts
                            if guess_state_abbr(part) is not None
                        ]
                    )
                ),
            },
            "filename": {
                "state_abbr": guess_state_abbr(filename),
                "year_part": guess_year_part(filename),
            },
            "element": {
                "state_abbr": guess_state_abbr(location.link_text),
                "state_name": guess_state_name(location.link_text),
                "year_part": guess_year_part(location.link_text),
            },
            "parent": {"state_abbr": guess_state_abbr(location.closest_heading)},
        }
        results.append(result)

    pp.pprint(results)

    # {
    #     pathname: {
    #         state,
    #         year,
    #         month
    #         lang
    #     },
    #     filename: {
    #         state,
    #         year,
    #         month
    #         lang
    #     }
    #     link: {
    #         state,
    #         year,
    #         month
    #         lang
    #     }
    #     closest_heading{
    #         state,
    #         year,
    #         month
    #         lang
    #     }

    # }
