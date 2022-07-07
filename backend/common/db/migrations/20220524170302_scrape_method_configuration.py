from beanie import iterative_migration
from backend.common.models.site import (
    ScrapeMethodConfiguration,
    LastStatusSite,
    NoScrapeConfigSite,
)


class Forward:
    @iterative_migration()
    async def create_scrape_config(
        self, input_document: NoScrapeConfigSite, output_document: LastStatusSite
    ):
        output_document.scrape_method_configuration = ScrapeMethodConfiguration(
            document_extensions=["pdf"],
            url_keywords=[],
        )


class Backward:
    @iterative_migration()
    async def remove_scrape_config(
        self, input_document: LastStatusSite, output_document: NoScrapeConfigSite
    ):
        output_document.scrape_method_configuration = None
