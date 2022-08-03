from beanie import iterative_migration

from backend.common.models.site_scrape_task import SiteScrapeTask


class Forward:
    @iterative_migration()
    async def add_user_id_to_site_scrape_task(
        self, input_document: SiteScrapeTask, output_document: SiteScrapeTask
    ):
        if not input_document.user_id:
            output_document.user_id = None


class Backward:
    @iterative_migration()
    async def remove_user_id_from_site_scrape_task(
        self, input_document: SiteScrapeTask, output_document: SiteScrapeTask
    ):
        output_document.user_id = None
