import logging
from functools import cached_property
from playwright.async_api import ElementHandle, Route, Request as RouteRequest
from backend.scrapeworker.common.models import Download, Metadata, Request
from backend.scrapeworker.common.selectors import filter_by_href
from backend.scrapeworker.strategies import playwright_mixins
from backend.scrapeworker.strategies.playwright_strategies.base_strategy import (
    BaseStrategy,
)


class AspNetWebFormStrategy(BaseStrategy):
    @cached_property
    def css_selector(self) -> str:
        href_selectors = filter_by_href(webform=True)
        return ", ".join(href_selectors)

    async def nav_to_page(self):
        cookie = {
            "name": "AspxAutoDetectCookieSupport",
            "value": "1",
            "domain": self.parsed_url.hostname,
            "path": "/",
            "httpOnly": True,
            "secure": True,
        }

        await self.context.add_cookies([cookie])
        await super().nav_to_page(timeout=60000)

    async def collect_downloads(
        self,
        elements: list[ElementHandle],
    ) -> list[Download]:
        requests: list[Request] = []
        metadatas: list[Metadata] = []
        downloads: list[Download] = []

        async def intercept(route: Route, request: RouteRequest):
            if self.url in request.url and request.method == "POST":
                logging.info(f"intercepted={request.url}")
                requests.append(
                    Request(
                        method=request.method,
                        url=request.url,
                        headers=request.headers,
                        data=request.post_data,
                    )
                )

            await route.continue_()

        await self.page.route("**/*", intercept)

        el: ElementHandle
        for el in elements:
            metadata = await playwright_mixins.extract_metadata(el)
            metadatas.append(metadata)
            await el.click(timeout=3000)

        await self.page.unroute("**/*", intercept)

        request: RouteRequest
        for index, request in enumerate(requests):
            if request:
                downloads.append(
                    Download(
                        metadata=metadata[index],
                        request=request,
                    )
                )

        return downloads

    async def execute(self):
        await self.nav_to_page()

        elements = await self.find_elements(self.css_selector)
        logging.info(f"elementsLength={len(elements)}")

        downloads = await self.collect_downloads(elements)
        logging.info(f"downloadsLength={len(downloads)}")

        return (elements, downloads)
