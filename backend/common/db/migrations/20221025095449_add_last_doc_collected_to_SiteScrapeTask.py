from beanie import free_fall_migration

from backend.common.models.site_scrape_task import SiteScrapeTask


class Forward:
    @free_fall_migration(document_models=[SiteScrapeTask])
    async def add_last_doc_collected_field(self, session):
        await SiteScrapeTask.get_motor_collection().update_many(
            {}, {"$set": {"last_doc_collected": None}}
        )


class Backward:
    pass
