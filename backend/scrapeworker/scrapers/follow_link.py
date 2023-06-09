from dataclasses import dataclass
from functools import cached_property

from playwright.async_api import Cookie, ElementHandle

from backend.scrapeworker.common.models import Metadata
from backend.scrapeworker.common.selectors import filter_by_href
from backend.scrapeworker.common.utils import normalize_url
from backend.scrapeworker.scrapers.playwright_base_scraper import PlaywrightBaseScraper


class FollowLinkScraper(PlaywrightBaseScraper):
    type: str = "FollowLink"

    @dataclass
    class FollowLink:
        url: str
        cookies: list[Cookie]
        link_text: str | None

        def __hash__(self):
            return hash(self.url)

    @cached_property
    def css_selector(self) -> str:
        href_selectors = filter_by_href(
            keywords=self.config.follow_link_keywords,
            url_keywords=self.config.follow_link_url_keywords,
        )
        self.selectors = self.selectors + href_selectors
        self.log.debug(self.selectors)
        return ", ".join(self.selectors)

    async def execute(self):
        follow_links: list[FollowLinkScraper.FollowLink] = []
        if not self.config.follow_links or not await self.is_applicable():
            return follow_links

        follow_handles = await self.page.query_selector_all(self.css_selector)
        base_tag_href = await self.get_base_href()

        follow_handle: ElementHandle
        for follow_handle in follow_handles:
            metadata: Metadata = await self.extract_metadata(follow_handle)
            url = normalize_url(self.url, metadata.resource_value, base_tag_href)
            cookies = await self.context.cookies()
            follow_links.append(self.FollowLink(url, cookies, metadata.link_text))
        return follow_links
