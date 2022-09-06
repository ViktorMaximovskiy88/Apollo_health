import asyncio
import logging
from functools import cached_property

from playwright.async_api import ElementHandle
from playwright.async_api import Response as PageResponse

from backend.scrapeworker.common.models import DownloadContext, Metadata, Request, Response
from backend.scrapeworker.common.selectors import to_xpath
from backend.scrapeworker.scrapers.playwright_base_scraper import PlaywrightBaseScraper


class JavascriptClick(PlaywrightBaseScraper):

    type: str = "Javascript"
    requests: list[Request | None] = []
    metadatas: list[Metadata] = []
    downloads: list[DownloadContext] = []
    links_found: int = 0
    last_metadata_index: int = 0

    @cached_property
    def css_selector(self) -> str | None:
        css_selectors = []
        return ",".join(css_selectors)

    @cached_property
    def xpath_selector(self) -> str:
        selectors = []
        for attr_selector in self.config.attr_selectors:
            if not attr_selector.resource_address:
                selectors.append(to_xpath(attr_selector))
        selector_string = "|".join(selectors)
        self.log.info(selector_string)
        return selector_string

    async def handle_json(self, response: PageResponse) -> DownloadContext | None:
        try:
            parsed = await response.json()
        except Exception:
            self.log.debug("no json response")
            return None
        content_type = response.headers["content-type"]
        if content_type == "application/vnd.contentful.delivery.v1+json":  # Contentful
            self.log.debug(f"follow json {content_type}")
            file_field = parsed["fields"]["file"]
            return DownloadContext(
                content_type=file_field["contentType"],
                request=Request(
                    url=f'https:{file_field["url"]}',
                    filename=file_field["fileName"],
                ),
            )
        elif "entry" in parsed and "content" in parsed["entry"]:  # WPS
            content_field = parsed["entry"]["content"]["resourceUri"]
            return DownloadContext(
                content_type=content_field["type"],
                request=Request(
                    url=f'https://{self.parsed_url.netloc}{content_field["value"]}',
                    filename=parsed["entry"]["title"]["value"],
                ),
            )
        return None

    async def execute(self) -> list[DownloadContext]:
        downloads: list[DownloadContext] = []
        link_handle: ElementHandle

        async def postprocess(response: PageResponse) -> None:
            accepted_types = [
                "application/pdf",
                "application/vnd.ms-excel",
                "application/msword",
            ]
            try:
                content_type: str | None = None

                # Handle click which responses with pdf or other media download.
                # AttributeError: 'Download' object has no attribute headers.
                # Tried if isinstance(content_type, Download):, but does not work.
                if not hasattr("response", "headers"):
                    self.log.debug(f"javascript click -> direct download {content_type}")
                    download = DownloadContext(
                        response=Response(content_type=content_type),
                        request=Request(
                            url=response.url,
                        ),
                    )
                    download.metadata = await self.extract_metadata(link_handle)
                    downloads.append(download)
                # Handle special json response.
                elif content_type == "application/vnd.contentful.delivery.v1+json":
                    if "content-type" in response.headers:
                        content_type = response.headers["content-type"]
                    if content_type in accepted_types:
                        await response.finished()
                        download = await self.handle_json(response)
                        if download:
                            download.metadata = await self.extract_metadata(link_handle)
                            downloads.append(download)
                    else:
                        self.log.debug(f"unknown format {content_type}")
            except Exception:
                logging.error("exception", exc_info=True)

        xpath_locator = self.page.locator(self.xpath_selector)
        xpath_locator_count = await xpath_locator.count()

        for index in range(0, xpath_locator_count):
            try:
                link_handle = await xpath_locator.nth(index).element_handle(timeout=1000)
                self.page.on("download", postprocess)
                self.page.on("response", postprocess)

                await link_handle.click()
                await asyncio.sleep(0.25)
            except Exception:
                logging.error("exception", exc_info=True)
                await self.page.goto(self.url)

        return downloads
