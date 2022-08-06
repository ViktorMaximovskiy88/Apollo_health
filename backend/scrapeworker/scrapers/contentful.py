import json
import logging
from functools import cached_property

from playwright.async_api import APIResponse

from backend.scrapeworker.common.models import DownloadContext, Metadata, Request, Response
from backend.scrapeworker.scrapers.playwright_base_scraper import PlaywrightBaseScraper


class ContentfulScraper(PlaywrightBaseScraper):

    type: str = "Contentful"
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
    def xpath_selector(self) -> str | None:
        xpaths_selectors = ['//a[@*[starts-with(name(), "data-v-")]][not(@href)]']
        return "|".join(xpaths_selectors)

    async def is_applicable(self) -> bool:
        parent_applicable = await super().is_applicable()
        # TODO best way to sniff this narrowly...
        return parent_applicable

    async def __postprocess(self, response: APIResponse) -> DownloadContext | None:
        parsed = None
        content_type = None
        try:
            content_type = response.headers["content-type"]
            if content_type == "application/vnd.contentful.delivery.v1+json":
                logging.debug(f"follow json {content_type}")
                body = await response.body()
                parsed = json.loads(body)
                file_field = parsed["fields"]["file"]

                return DownloadContext(
                    content_type=file_field["contentType"],
                    request=Request(
                        url=f'https:{file_field["url"]}',
                        filename=file_field["fileName"],
                    ),
                )
            elif "assets" in response.url:
                logging.debug(f"direct download {content_type}")
                return DownloadContext(
                    response=Response(content_type=content_type, status=response.status),
                    request=Request(
                        url=response.url,
                    ),
                )
            else:
                logging.debug(f"not contentful {content_type}")
                return None

        except Exception:
            logging.error("exception", exc_info=1)
            return None

    async def execute(self) -> list[DownloadContext]:
        downloads: list[DownloadContext] = []

        xpath_locator = self.page.locator(self.xpath_selector)
        xpath_locator_count = await xpath_locator.count()

        for index in range(0, xpath_locator_count):
            try:
                link_handle = await xpath_locator.nth(index).element_handle(timeout=1000)
                async with self.page.expect_event("response", timeout=1000) as event_info:

                    await link_handle.click()
                    response: APIResponse = await event_info.value

                    if not response:
                        continue

                    download = await self.__postprocess(response)

                    if not download:
                        continue

                    download.metadata = await self.extract_metadata(link_handle)
                    download.metadata.href = response.url

                    downloads.append(download)

            except Exception:
                logging.error("exception", exc_info=1)
                await self.page.goto(self.url)

        return downloads
