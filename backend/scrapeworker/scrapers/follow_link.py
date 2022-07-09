import logging
from functools import cached_property
from playwright.async_api import ElementHandle
from backend.scrapeworker.common.models import Download, Metadata, Request
from backend.scrapeworker.common.selectors import filter_by_href
from backend.scrapeworker.scrapers.playwright_base_scraper import PlaywrightBaseScraper
from urllib.parse import urljoin


class FollowLinkScraper(PlaywrightBaseScraper):
    type: str = "FollowLink"

    async def is_applicable(self) -> bool:
        return bool(self.config.follow_links)

    @cached_property
    def css_selector(self) -> str:
        href_selectors = filter_by_href(
            keywords=self.config.follow_link_keywords,
            url_keywords=self.config.follow_link_url_keywords,
        )
        self.selectors = self.selectors + href_selectors
        logging.debug(self.selectors)
        return ", ".join(self.selectors)

    async def execute(self) -> list[Download]:
        urls: list[Download] = []

        follow_handles = await self.page.query_selector_all(self.css_selector)

        follow_handle: ElementHandle
        for follow_handle in follow_handles:
            metadata: Metadata = await self.extract_metadata(follow_handle)
            urls.append(
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
        return urls
