import logging
import asyncio
from backend.scrapeworker.models import Download, Metadata, Request
from backend.scrapeworker.drivers.playwright.base_driver import PlaywrightDriver
from urllib.parse import urlparse
from playwright.async_api import ElementHandle, Request as RouteRequest, Route
from playwright_stealth import stealth_async


class AspWebForm(PlaywrightDriver):
    
    async def navigate(self, url):
        self.url = url
        await stealth_async(self.page)
        parsed_url = urlparse(self.url)
        cookie = {
            'name': 'AspxAutoDetectCookieSupport',
            'value': '1',
            'domain': parsed_url.hostname,
            'path': '/',
            'httpOnly': True,
            'secure': True,
        }

        await self.context.add_cookies([cookie])
        await self.page.goto(self.url, wait_until="domcontentloaded")

    async def collect(self, elements: list[ElementHandle]) -> list[Download]:
        requests = []
        metadata = []
 
        async def intercept(route: Route, request: RouteRequest):
            print(request)
            route.abort()
            
        await self.page.route(f'{self.url}*', intercept)

        # TODO if a page route click doesnt nav... 
        # handle error case somehow...
        el: ElementHandle
        for el in elements:
            text, _ = await asyncio.gather(
                el.text_content(),
                el.click()
            )
            metadata.append(Metadata(text=text))

        # zip them together
        downloads = []
        for index, request in enumerate(requests):
            downloads.append(
                Download(
                    metadata=metadata[index],
                    request=request,
                )
            )
        
        return downloads
