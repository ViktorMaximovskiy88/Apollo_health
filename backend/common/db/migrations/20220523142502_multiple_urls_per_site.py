from beanie import iterative_migration
from backend.common.models.site import BaseUrl, NoScrapeConfigSite, SingleUrlSite


class Forward:
    @iterative_migration()
    async def url_to_urls(
        self, input_document: SingleUrlSite, output_document: NoScrapeConfigSite
    ):
        if input_document.base_url == None:
            return
        output_document.base_urls = [BaseUrl(url=input_document.base_url)]


class Backward:
    @iterative_migration()
    async def urls_to_url(
        self, input_document: NoScrapeConfigSite, output_document: SingleUrlSite
    ):
        output_document.base_url = input_document.base_urls[0].url
