import logging
from functools import cached_property
from urllib.parse import urljoin

from playwright.async_api import ElementHandle

from backend.scrapeworker.common.models import DownloadContext, Metadata, Request
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

        self.selectors = self.selectors + href_selectors + hidden_value_selectors
        selector_string = ", ".join(self.selectors)
        logging.info(selector_string)
        return selector_string

    async def queue_downloads(
        self, downloads: list[DownloadContext], link_handles: list[ElementHandle], base_url: str
    ) -> None:
        link_handle: ElementHandle
        for link_handle in link_handles:
            metadata: Metadata = await self.extract_metadata(link_handle)
            downloads.append(
                DownloadContext(
                    metadata=metadata,
                    request=Request(
                        url=urljoin(
                            base_url,
                            metadata.href,
                        ),
                    ),
                )
            )

    async def execute(self) -> list[DownloadContext]:
        downloads: list[DownloadContext] = []

        link_handles = await self.page.query_selector_all(self.css_selector)
        await self.queue_downloads(downloads, link_handles, self.page.url)

        # handle frame (not frames, although we could....)
        if len(self.page.main_frame.child_frames) > 0 and self.config.search_in_frames:
            child_frames = self.page.main_frame.child_frames
            link_handles += await child_frames[0].query_selector_all(self.css_selector)
            await self.queue_downloads(downloads, link_handles, child_frames[0].url)

        return downloads
