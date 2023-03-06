from functools import cached_property
from urllib.parse import ParseResult, urlparse

from backend.common.models.site import ScrapeMethodConfiguration
from backend.scrapeworker.common.models import DownloadContext, Metadata, Request
from backend.scrapeworker.common.selectors import filter_by_href
from backend.scrapeworker.scrapers.playwright_base_scraper import PlaywrightBaseScraper


class HumanaScraper(PlaywrightBaseScraper):

    type: str = "Humana"
    downloads: list[DownloadContext] = []

    @staticmethod
    def scrape_select(url, config: ScrapeMethodConfiguration | None = None) -> bool:
        parsed_url: ParseResult = urlparse(url)
        result = parsed_url.netloc == "apps.humana.com"
        return result

    @cached_property
    def css_selector(self) -> str:
        self.selectors = filter_by_href(webform=True)
        selector_string = ", ".join(self.selectors)
        self.log.info(selector_string)
        return selector_string

    async def is_applicable(self) -> bool:
        self.log.debug(f"self.parsed_url.netloc={self.parsed_url.netloc}")
        result = self.parsed_url.netloc in ["apps.humana.com"]
        self.log.info(f"{self.__class__.__name__} is_applicable -> {result}")
        return result

    async def execute(self) -> list[DownloadContext]:
        downloads: list[DownloadContext] = []
        link_handles = await self.page.query_selector_all(self.css_selector)
        for link_handle in link_handles:
            metadata: Metadata = await self.extract_metadata(link_handle)
            metadata.base_url = self.page.url
            name: str = await link_handle.get_attribute("name")
            url = f"https://dctm.humana.com/Mentor/Web/v.aspx?objectID={name}&dl=1"
            downloads.append(DownloadContext(metadata=metadata, request=Request(url=url)))

        return downloads
