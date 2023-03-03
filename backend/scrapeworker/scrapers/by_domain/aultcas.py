import asyncio
import logging
import os
import re
from functools import cached_property
from urllib.parse import ParseResult, urlparse

from playwright._impl._api_structures import SetCookieParam
from playwright.async_api import Download, ElementHandle, Locator
from playwright.async_api import Request as RouteRequest
from playwright.async_api import Route
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from backend.scrapeworker.common.models import DownloadContext, Metadata, Request, Response
from backend.scrapeworker.common.selectors import filter_by_href, to_xpath
from backend.scrapeworker.scrapers.playwright_base_scraper import PlaywrightBaseScraper


class AultcasScraper(PlaywrightBaseScraper):

    type: str = "Aultcas"
    requests: list[Request | None] = []
    metadatas: list[Metadata] = []
    downloads: list[DownloadContext] = []
    links_found: int = 0
    last_metadata_index: int = 0

    @staticmethod
    def scrape_select(url, config: None = None) -> bool:
        parsed_url: ParseResult = urlparse(url)
        result = parsed_url.netloc == "www.aultcas.com"
        return result

    @cached_property
    def css_selector(self) -> str:
        href_selectors = filter_by_href(webform=True)
        return ", ".join(href_selectors)

    @cached_property
    def xpath_selector(self) -> str:
        selectors = []
        for attr_selector in self.config.attr_selectors:
            if not attr_selector.resource_address:
                selectors.append(to_xpath(attr_selector))
        selector_string = "|".join(selectors)
        self.log.info(selector_string)
        return selector_string

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
        element_id: str
        self.log.debug(f"interacting {self.url}")

        async def intercept(route: Route, request: RouteRequest):
            # Handle post
            if self.url in request.url and request.method == "POST":
                self.log.debug(f"queueing {element_id}")
                self.requests.append(
                    Request(
                        url=request.url,
                        method=request.method,
                        headers=request.headers,
                        data=request.post_data,
                        filename=element_id,
                    )
                )
                await route.continue_()
            else:
                await route.abort()

        async def postprocess_download(download: Download) -> None:
            accepted_types = [".pdf", ".xls", ".xlsx", ".doc", ".docx"]
            try:
                # Response may not always have content-type header.
                # Use filename ext instead.
                # suggested_filename='PriorAuthorization.pdf'
                filename, file_extension = os.path.splitext(download.suggested_filename)
                if file_extension in accepted_types:
                    self.log.debug(f"asp -> direct download: {filename}.{file_extension}")
                    download = DownloadContext(
                        response=Response(content_type=None),
                        request=Request(
                            url=download.url,
                        ),
                    )
                    download.metadata = await self.extract_metadata(link_handle)
                    self.downloads.append(download)
                else:
                    self.log.debug(f"unknown download extension: {file_extension}")
                    return None
            except Exception:
                logging.error("exception", exc_info=True)

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
                        self.log.debug(f"Max retries reached {element_id}")
                    continue
            return

        await self.page.route("**/*", intercept)

        if self.config.attr_selectors:
            self.page.on("download", postprocess_download)
            xpath_locator = self.page.locator(self.xpath_selector)
            xpath_locator_count = await xpath_locator.count()
            for index in range(0, xpath_locator_count):
                try:
                    link_handle = await xpath_locator.nth(index).element_handle(timeout=1000)
                    await link_handle.click()
                    await asyncio.sleep(0.25)
                except Exception:
                    logging.error("exception", exc_info=True)
                    await self.page.goto(self.url)
        else:
            self.page.on("download", lambda download: download.cancel())
            metadata: Metadata
            for index, metadata in enumerate(self.metadatas):
                if not metadata.element_id:
                    continue
                element_id = re.sub(r"(?u)[^-\w.]", "_", metadata.element_id)
                locator: Locator = self.page.locator(f"#{metadata.element_id}")
                await click_with_backoff(locator)

            await self.page.unroute("**/*", intercept)

    async def __process(self):
        for index, request in enumerate(self.requests):
            if request:
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
