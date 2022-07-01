import logging
from functools import cached_property
from playwright.async_api import (
    ElementHandle,
    Route,
    Request as RouteRequest,
)
from backend.scrapeworker.common.models import Download, Metadata, Request
from backend.scrapeworker.common.selectors import filter_by_href
from backend.scrapeworker.strategies.playwright_strategies.base_strategy import (
    BaseStrategy,
)
from backend.scrapeworker.strategies import playwright_mixins


class AspNetWebFormStrategy(BaseStrategy):

    type: str = "AspNetWebForm"

    @cached_property
    def css_selector(self) -> str:
        href_selectors = filter_by_href(webform=True)
        return ", ".join(href_selectors)

    async def setup(self):
        cookie = {
            "name": "AspxAutoDetectCookieSupport",
            "value": "1",
            "domain": self.parsed_url.hostname,
            "path": "/",
            "httpOnly": True,
            "secure": True,
        }

        await self.context.add_cookies([cookie])

    async def execute(self) -> list[Download]:
        requests: list[Request] = []
        metadatas: list[Metadata] = []
        downloads: list[Download] = []

        await self.setup()

        link_handles = await self.page.query_selector_all(self.css_selector)

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

        link_handle: ElementHandle
        for link_handle in link_handles:
            metadata = await playwright_mixins.extract_metadata(link_handle)
            metadatas.append(metadata)
            await link_handle.click()

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
