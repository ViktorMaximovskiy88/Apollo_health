from functools import cached_property

from backend.scrapeworker.common.models import DownloadContext
from backend.scrapeworker.common.selectors import to_xpath
from backend.scrapeworker.scrapers.playwright_base_scraper import PlaywrightBaseScraper


class TargetedHtmlScraper(PlaywrightBaseScraper):
    # use attribute selector to target section to scrape
    # use exclude selectors to exclude from that section

    # will have attr selectors
    # will have exclude selectors
    type: str = "TargetedHTML"

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

    async def execute(self) -> list[DownloadContext]:
        # for each selector, extract html, remove excludes, and save the html
        pass
