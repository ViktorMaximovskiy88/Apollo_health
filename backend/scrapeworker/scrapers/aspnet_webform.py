import asyncio
import logging
from functools import cached_property

from playwright._impl._api_structures import SetCookieParam
from playwright.async_api import APIResponse, ElementHandle, Locator
from playwright.async_api import Request as RouteRequest
from playwright.async_api import Route
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from backend.scrapeworker.common.models import DownloadContext, Metadata, Request
from backend.scrapeworker.common.selectors import filter_by_href
from backend.scrapeworker.scrapers.playwright_base_scraper import PlaywrightBaseScraper


class AspNetWebFormScraper(PlaywrightBaseScraper):

    type: str = "AspNetWebForm"
    requests: list[Request | None] = []
    metadatas: list[Metadata] = []
    downloads: list[DownloadContext] = []
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

        async def click_with_backoff(locator: Locator, max_retries: int = 2) -> None:
            for retry in range(0, max_retries + 1):
                try:
                    timeout = 30000
                    if retry > 0:
                        wait = (retry + 1) ** 3
                        timeout *= retry
                        await asyncio.sleep(wait)
                    await locator.click(timeout=timeout)
                    return
                except PlaywrightTimeoutError:
                    if retry == max_retries:
                        logging.debug("Max retries reached")
                    continue
            return

        await self.page.route("**/*", intercept)

        metadata: Metadata
        for index, metadata in enumerate(self.metadatas):
            logging.debug(f"{index} of {len(self.metadatas)} count of metadata")
            if not metadata.element_id:
                continue
            locator: Locator = self.page.locator(f"#{metadata.element_id}")
            await click_with_backoff(locator)

        await self.page.unroute("**/*", intercept)

    async def __process(self):
        for index, request in enumerate(self.requests):
            if request:
                logging.info(f"#{index} downloading filename={request.filename}")
                self.downloads.append(
                    DownloadContext(
                        metadata=self.metadatas[index],
                        request=request,
                    )
                )

    async def execute(self) -> list[DownloadContext]:

        await self.__setup()
        await self.__gather()
        await self.__interact()
        await self.__process()

        return self.downloads
