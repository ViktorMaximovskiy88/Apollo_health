import logging
from backend.scrapeworker.common.models import Download, Metadata, Request
from backend.scrapeworker.drivers.playwright.playwright_driver import PlaywrightDriver
from urllib.parse import urlparse
from playwright.async_api import ElementHandle
from playwright_stealth import stealth_async
from urllib.parse import urlparse


class PlaywrightWordPressAjax(PlaywrightDriver):
    async def nav_to_page(self, url):
        self.url = url
        self.parsed_url = urlparse(url)

        await stealth_async(self.page)

        json_docs = []

        async def intercept(route, request):
            if "/wp-admin/admin-ajax.php" in request.url:
                print("intercept continue", request)
                json_docs.append(request)
            await route.continue_()

        await self.page.route("**/*", intercept)
        await self.page.goto(self.url, wait_until="domcontentloaded")

    async def collect_downloads(self, elements: list[ElementHandle]) -> list[Download]:
        metadata: list[Metadata] = []
        logging.debug(f"extract_metadata")
        for el in elements:
            meta = await self.extract_metadata(el)
            metadata.append(meta)

        downloads: list[Download] = []
        return downloads
