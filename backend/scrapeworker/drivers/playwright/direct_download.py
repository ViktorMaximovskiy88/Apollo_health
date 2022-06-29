import urllib.parse
from backend.scrapeworker.common.models import Download, Request
from backend.scrapeworker.drivers.playwright.playwright_driver import PlaywrightDriver
from playwright.async_api import ElementHandle
from playwright_stealth import stealth_async


class PlaywrightDirectDownload(PlaywrightDriver):
    async def nav_to_page(self, url) -> None:
        self.url = url
        await stealth_async(self.page)
        await self.page.goto(url, wait_until="domcontentloaded")

    async def collect_downloads(self, elements: list[ElementHandle]) -> list[Download]:
        downloads = []

        el: ElementHandle
        for el in elements:
            metadata = await self.extract_metadata(el)
            downloads.append(
                Download(
                    metadata=metadata,
                    request=Request(
                        method="GET",
                        url=urllib.parse.urljoin(self.url, metadata.href),
                    ),
                )
            )

        return downloads
