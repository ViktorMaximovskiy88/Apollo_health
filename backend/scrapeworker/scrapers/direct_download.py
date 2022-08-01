import logging
from functools import cached_property
from urllib.parse import urljoin

from playwright.async_api import ElementHandle

from backend.scrapeworker.common.models import Download, Metadata, Request
from backend.scrapeworker.common.selectors import filter_by_hidden_value, filter_by_href
from backend.scrapeworker.scrapers.playwright_base_scraper import PlaywrightBaseScraper


class DirectDownloadScraper(PlaywrightBaseScraper):
    type: str = "DirectDownload"

    @cached_property
    def css_selector(self) -> str:
        href_selectors = filter_by_href(
            extensions=self.config.document_extensions,
            url_keywords=self.config.url_keywords,
        )

        hidden_value_selectors = filter_by_hidden_value(
            extensions=self.config.document_extensions,
            url_keywords=self.config.url_keywords,
        )

        selectors = href_selectors + hidden_value_selectors
        logging.debug(selectors)
        return ", ".join(selectors)

    @cached_property
    def xpath_selector(self) -> str:
        vue_anchors = ['//a[@*[starts-with(name(), "data-v")]][not(@href)]']
        return "|".join(vue_anchors)

    async def execute(self) -> list[Download]:
        downloads: list[Download] = []

        link_handles = await self.page.query_selector_all(self.css_selector)

        xpath_locator_count = 0
        if self.xpath_selector:
            xpath_locator = self.page.locator(self.xpath_selector)
            xpath_locator_count = await xpath_locator.count()
            for index in range(0, xpath_locator_count):
                try:
                    link_handle = await xpath_locator.nth(index).element_handle()

                    async with self.page.expect_event("download", timeout=2000):
                        await link_handle.click()

                        async with self.page.expect_event("response", timeout=2000) as event_info:
                            response = await event_info.value
                            metadata: Metadata = await self.extract_metadata(link_handle)
                            metadata.href = response.url

                            print(response, link_handle, metadata)

                            downloads.append(
                                Download(
                                    metadata=metadata,
                                    request=Request(url=response.url),
                                )
                            )

                except Exception as ex:
                    print(ex, " **** *** ")
                    await self.page.goto(self.url)

        link_handle: ElementHandle
        for link_handle in link_handles:
            metadata: Metadata = await self.extract_metadata(link_handle)
            downloads.append(
                Download(
                    metadata=metadata,
                    request=Request(
                        url=urljoin(
                            self.url,
                            metadata.href,
                        ),
                    ),
                )
            )

        return downloads
