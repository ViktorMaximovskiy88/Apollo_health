from aiohttp import ClientSession

from backend.scrapeworker.common.models import DownloadContext, Metadata, Request
from backend.scrapeworker.scrapers.playwright_base_scraper import PlaywrightBaseScraper


class ParFormularyNavigatorScraper(PlaywrightBaseScraper):

    type: str = "ParFormularyNavigatorScraper"
    downloads: list[DownloadContext] = []

    async def is_applicable(self) -> bool:
        self.log.debug(f"self.parsed_url.netloc={self.parsed_url.netloc}")
        result = self.parsed_url.netloc in ["fn-doc-api.mmitnetwork.com"]
        self.log.info(f"{self.__class__.__name__} is_applicable -> {result}")
        return result

    async def fetch_urls(self, base_url) -> list[str]:
        headers = {
            "content-type": "application/json",
            "api-key": "foo",  # TODO use `real` env var
        }

        async with ClientSession() as session:
            async with session.request(
                url=base_url,
                method="GET",
                headers=headers,
            ) as response:
                result = await response.json()
                return result

    async def execute(self) -> list[DownloadContext]:
        downloads: list[DownloadContext] = []
        for url in await self.fetch_urls(self.url):
            downloads.append(DownloadContext(metadata=Metadata(), request=Request(url=url)))
        return downloads
