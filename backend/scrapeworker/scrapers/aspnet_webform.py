import logging
from functools import cached_property
from playwright.async_api import (
    ElementHandle,
    Route,
    Request as RouteRequest,
    APIResponse,
    Error,
    Locator,
)
from playwright._impl._api_structures import SetCookieParam
from backend.scrapeworker.common.models import Download, Metadata, Request
from backend.scrapeworker.common.selectors import filter_by_href
from backend.scrapeworker.scrapers.playwright_base_scraper import PlaywrightBaseScraper


class AspNetWebFormScraper(PlaywrightBaseScraper):

    type: str = "AspNetWebForm"
    requests: list[Request | None] = []
    metadatas: list[Metadata] = []
    downloads: list[Download] = []
    links_found: int = 0
    last_metadata_index: int = 0

    @cached_property
    def css_selector(self) -> str:
        href_selectors = filter_by_href(webform=True)
        return ", ".join(href_selectors)

    async def __setup(self):
        cookie: SetCookieParam = {
            "name": "AspxAutoDetectCookieSupport",
            "value": "1",
            "domain": self.parsed_url.hostname,
            "path": "/",
            "httpOnly": True,
            "secure": True,
        }

        await self.context.add_cookies([cookie])

    async def __gather(self):
        self.link_handles = await self.page.query_selector_all(self.css_selector)
        self.links_found = len(self.link_handles)

        link_handle: ElementHandle
        for index, link_handle in enumerate(self.link_handles):
            print(f"#{index} metadata link")
            metadata = await self.extract_metadata(link_handle)
            self.metadatas.append(metadata)

    async def __interact(self) -> None:
        async def intercept(route: Route, request: RouteRequest):
            if self.url in request.url and request.method == "POST":
                response: APIResponse = await self.page.request.fetch(
                    request.url,
                    headers=request.headers,
                    data=request.post_data,
                    method=request.method,
                )

                if filename := response.headers.get("content-disposition"):
                    logging.info(f"filename={filename}")
                    self.requests.append(
                        Request(
                            url=request.url,
                            method=request.method,
                            headers=request.headers,
                            data=request.post_data,
                            filename=filename,
                        )
                    )
                else:
                    self.requests.append(None)

                await route.continue_()
            else:
                await route.abort()

        await self.page.route("**/*", intercept)

        metadata: Metadata
        for index, metadata in enumerate(self.metadatas):
            logging.debug(f"{index} of {len(self.metadatas)} count of metadata")
            locator: Locator = self.page.locator(f"#{metadata.element_id}")
            await locator.click()

        await self.page.unroute("**/*", intercept)

    async def __process(self):
        for index, request in enumerate(self.requests):
            if request:
                logging.info(f"#{index} downloading filename={request.filename}")
                self.downloads.append(
                    Download(
                        metadata=self.metadatas[index],
                        request=request,
                    )
                )

    async def execute(self) -> list[Download]:

        await self.__setup()
        await self.__gather()
        await self.__interact()
        await self.__process()

        return self.downloads
