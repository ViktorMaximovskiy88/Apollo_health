from beanie import free_fall_migration

from backend.common.models.site import Site


class Forward:
    @free_fall_migration(document_models=[Site])
    async def add_scrape_base_page(self, session):
        Site.get_motor_collection().update_many(
            {
                "scrape_method_configuration.follow_links": True,
                "$or": [
                    {"scrape_method_configuration.scrape_base_page": None},
                    {"scrape_method_configuration.scrape_base_page": {"$exists": False}},
                ],
            },
            {"$set": {"scrape_method_configuration.scrape_base_page": True}},
        )


class Backward:
    ...
