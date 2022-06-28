import logging
import asyncio
import urllib.parse
from backend.scrapeworker.common.models import Download, Metadata, Request
from backend.scrapeworker.drivers.playwright.base_driver import PlaywrightDriver
from playwright.async_api import ElementHandle
from playwright_stealth import stealth_async


class DirectDownload(PlaywrightDriver):
    async def navigate(self, url):
        self.url = url
        await stealth_async(self.page)
        await self.page.goto(url, wait_until="domcontentloaded")
        
    async def collect(self, elements: list[ElementHandle]) -> list[Download]:
        downloads = []
        
        el: ElementHandle
        for el in elements:
            text, href = await asyncio.gather(
                el.text_content(),
                el.get_attribute('href'),
            )
            
            downloads.append(
                Download(
                    metadata=Metadata(text=text.strip()),
                    request=Request(
                        method="GET",
                        url=urllib.parse.urljoin(self.url, href),
                    )
                )
            )

        return downloads
