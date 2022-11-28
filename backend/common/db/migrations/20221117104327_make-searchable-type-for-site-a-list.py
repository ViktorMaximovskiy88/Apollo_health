from beanie import free_fall_migration

from backend.common.models.site import Site
from backend.common.models.site_scrape_task import SiteScrapeTask


class Forward:
    @free_fall_migration(document_models=[Site])
    async def make_searchable_type_for_site_a_list(self, session):
        await Site.get_motor_collection().update_many(
            {"scrape_method_configuration.searchable_type": {"$in": ["CPTCODES", "JCODES"]}},
            [
                {
                    "$set": {
                        "scrape_method_configuration.searchable_type": [
                            "$scrape_method_configuration.searchable_type"
                        ]
                    }
                }
            ],
        )

        await Site.get_motor_collection().update_many(
            {"scrape_method_configuration.searchable_type": None},
            {"scrape_method_configuration.searchable_type": []},
        )

        await SiteScrapeTask.get_motor_collection().update_many(
            {},
            [
                {
                    "$set": {
                        "scrape_method_configuration.searchable_type": [
                            "$scrape_method_configuration.searchable_type"
                        ]
                    }
                }
            ],
        )


class Backward:
    @free_fall_migration(document_models=[Site])
    async def make_searchable_type_for_site_a_str(self, session):
        await Site.get_motor_collection().update_many(
            {},
            {
                "$set": {
                    "scrape_method_configuration.searchable_type": {
                        "$scrape_method_configuration.searchable_type"
                    }
                }
            },
        )

        await SiteScrapeTask.get_motor_collection().update_many(
            {},
            {
                "$set": {
                    "scrape_method_configuration.searchable_type": {
                        "$scrape_method_configuration.searchable_type"
                    }
                }
            },
        )
