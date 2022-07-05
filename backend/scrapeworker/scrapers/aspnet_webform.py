import logging
from functools import cached_property
from playwright.async_api import (
    ElementHandle,
    Route,
    Request as RouteRequest,
    Error,
)
from backend.scrapeworker.common.models import Download, Metadata, Request
from backend.scrapeworker.common.selectors import filter_by_href
from backend.scrapeworker.scrapers.playwright_base_scraper import PlaywrightBaseScraper


class AspNetWebFormScraper(PlaywrightBaseScraper):

    type: str = "AspNetWebForm"
    previous_element_id: str

    @cached_property
    def css_selector(self) -> str:
        href_selectors = filter_by_href(webform=True)
        return ", ".join(href_selectors)

    async def __setup(self):
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
        errors: list[str] = []

        try:
            await self.__execute()
        except Exception as ex:
            logging.error(ex)
            errors.append(self.previous_element_id)
            await self.__execute()

    async def __execute(self) -> list[Download]:
        requests: list[Request] = []
        metadatas: list[Metadata] = []
        downloads: list[Download] = []

        await self.__setup()
        link_handles = await self.page.query_selector_all(self.css_selector)

        async def intercept(route: Route, request: RouteRequest):
            if self.url in request.url and request.method == "POST":
                requests.append(
                    Request(
                        url=request.url,
                        method=request.method,
                        headers=request.headers,
                        data=request.post_data,
                    )
                )
                await route.continue_()
            else:
                await route.abort()

        await self.page.route("**/*", intercept)

        link_handle: ElementHandle
        for link_handle in link_handles:
            metadata = await self.extract_metadata(link_handle)
            metadatas.append(metadata)
            self.previous_element_id = metadata.element_id
            print(self.previous_element_id)
            await link_handle.click()

        await self.page.unroute("**/*", intercept)

        request: RouteRequest
        for index, request in enumerate(requests):
            if request:
                print(index)
                downloads.append(
                    Download(
                        metadata=metadata[index],
                        request=request,
                    )
                )

        return downloads
