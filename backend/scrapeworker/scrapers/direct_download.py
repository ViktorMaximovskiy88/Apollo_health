from functools import cached_property

from playwright.async_api import ElementHandle, Page

from backend.scrapeworker.common.models import DownloadContext, Metadata, Request
from backend.scrapeworker.common.selectors import filter_by_hidden_value, filter_by_href, to_xpath
from backend.scrapeworker.common.utils import normalize_url
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

        self.selectors = self.selectors + href_selectors + hidden_value_selectors
        selector_string = ", ".join(self.selectors)
        self.log.info(selector_string)
        return selector_string

    @cached_property
    def xpath_selector(self) -> str:
        selectors = []
        for attr_selector in self.config.attr_selectors:
            if attr_selector.resource_address:
                selectors.append(to_xpath(attr_selector))
        selector_string = "|".join(selectors)
        self.log.info(selector_string)
        return selector_string

    def xpath_selectors(self):
        for attr_selector in self.config.attr_selectors:
            if attr_selector.resource_address:
                yield to_xpath(attr_selector), attr_selector.attr_name

    async def queue_downloads(
        self,
        downloads: list[DownloadContext],
        link_handles: list[ElementHandle],
        base_url: str,
        resource_attr: str = "href",
    ) -> None:
        link_handle: ElementHandle
        base_tag_href = await self.get_base_href()
        cookies = await self.context.cookies(base_url)
        for link_handle in link_handles:
            metadata: Metadata = await self.extract_metadata(link_handle, resource_attr)
            url = normalize_url(base_url, metadata.resource_value, base_tag_href)
            metadata.base_url = base_url
            downloads.append(
                DownloadContext(metadata=metadata, request=Request(url=url, cookies=cookies))
            )

    async def scrape_and_queue(self, downloads: list[DownloadContext], page: Page) -> None:

        link_handles = await page.query_selector_all(self.css_selector)
        await self.queue_downloads(downloads, link_handles, self.page.url)

        for selector, attr_name in self.xpath_selectors():
            link_handles = await page.query_selector_all(selector)
            await self.queue_downloads(downloads, link_handles, self.page.url, attr_name)

    async def execute(self) -> list[DownloadContext]:
        downloads: list[DownloadContext] = []

        await self.scrape_and_queue(downloads, page=self.page)
        # handle frame (not frames, although we could....)
        if len(self.page.main_frame.child_frames) > 0 and self.config.search_in_frames:
            child_frames = self.page.main_frame.child_frames
            await self.scrape_and_queue(downloads, page=child_frames[0].page)

        return downloads
