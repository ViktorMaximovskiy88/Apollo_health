import logging
import asyncio
from backend.scrapeworker.common.models import Download, Metadata, Request
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


    async def action(self, el: ElementHandle, metadata=[]):
        text = await el.text_content()
        await el.click()
        metadata.append(Metadata(text=text))

    async def collect(self, elements: list[ElementHandle]) -> list[Download]:
        requests: list[Request] = []
        metadata: list[Metadata] = []
 
        # route handler
        async def intercept(route: Route, request: RouteRequest):                       
            print(request.url, "aa")
            headers = await request.all_headers()
            requests.append(
                Request(
                    url=request.url,
                    headers=headers,
                    body=request.post_data,
                    method=request.method,
                )
            )
            await route.abort()

        # intercept webform actions
        await self.page.route('**/*', intercept)
        tasks = [self.action(el, metadata=metadata) for el in elements]
        await asyncio.gather(*tasks)
        await self.page.unroute('**/*')

        # zip them together
        downloads: list[Download] = []
        for index, request in enumerate(requests):
            downloads.append(
                Download(
                    metadata=metadata[index],
                    request=request,
                )
            )

        return downloads
