from beanie import free_fall_migration

from backend.common.models.site_scrape_task import SiteScrapeTask


class Forward:
    @free_fall_migration(document_models=[SiteScrapeTask])
    async def add_scrape_attempt_count(self, session):
        SiteScrapeTask.get_motor_collection().update_many(
            {"attempt_count": {"$exists": False}}, {"$set": {"attempt_count": 0}}
        )


class Backward:
    ...
