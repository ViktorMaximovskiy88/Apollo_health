import logging
from backend.scrapeworker.common.models import Download, Metadata, Request
from backend.scrapeworker.drivers.playwright.playwright_driver import PlaywrightDriver
from urllib.parse import urlparse
from playwright.async_api import ElementHandle
from playwright_stealth import stealth_async
from urllib.parse import urlparse


class PlaywrightAspWebForm(PlaywrightDriver):
    async def nav_to_page(self, url):
        self.url = url
        await stealth_async(self.page)
        parsed_url = urlparse(self.url)
        cookie = {
            "name": "AspxAutoDetectCookieSupport",
            "value": "1",
            "domain": parsed_url.hostname,
            "path": "/",
            "httpOnly": True,
            "secure": True,
        }

        await self.context.add_cookies([cookie])
        await self.page.goto(self.url, wait_until="domcontentloaded")

    async def collect_downloads(self, elements: list[ElementHandle]) -> list[Download]:
        metadata: list[Metadata] = []
        logging.debug(f"extract_metadata")
        for el in elements:
            meta = await self.extract_metadata(el)
            metadata.append(meta)

        def handler(request):
            return self.url in request.url and request.method == "post"

        downloads: list[Download] = []
        for el in elements:
            logging.info(meta)
            async with self.page.expect_navigation() as event:
                logging.info(f"#{el} about to be clicked")
                await el.click()
                logging.info(f"#{meta.element_id} was clicked")

                response = await event.value
                # headers = await request.all_headers()

                print(response)

                logging.info(f"and then whatttt")
                # downloads.append(
                #     Download(
                #         metadata=meta,
                #         request=Request(
                #             method=request.method,
                #             headers=headers,
                #             url=request.url,
                #             data=request.post_data,
                #         ),
                #     )
                # )

        return downloads
