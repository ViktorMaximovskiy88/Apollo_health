import logging
import asyncio
from backend.scrapeworker.common.models import Download, Metadata, Request
from backend.scrapeworker.drivers.playwright.base_driver import PlaywrightDriver
from urllib.parse import urlparse
from playwright.async_api import ElementHandle
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
        text, _ = await asyncio.gather(el.text_content(), el.click())
        print('before url', text, self.url)
        metadata.append(Metadata(text=text))
        print(len(metadata))
        await self.page.wait_for_timeout(2000)
        print('after url', self.url)
        

    async def collect(self, elements: list[ElementHandle]) -> list[Download]:
        metadata: list[Metadata] = []
        for el in elements:
            id, text = await asyncio.gather(el.get_attribute("id"), el.text_content()) 
            metadata.append(Metadata(text=text,id=f'#{id}'))
        
        downloads: list[Download] = []
        for meta in metadata:            
            async with self.page.expect_request(self.url) as event:
                await self.page.locator(meta.id).click();
            
            request = await event.value
            headers = await request.all_headers()
            
            downloads.append(
                Download(
                    metadata=meta,
                    request=Request(
                        method=request.method,
                        headers=headers,
                        url=request.url,
                        data=request.post_data,
                    ),
                )
            )
            

        return downloads
