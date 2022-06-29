import logging
from functools import cached_property
from backend.scrapeworker.drivers.playwright.word_press_ajax import (
    PlaywrightWordPressAjax,
)
from backend.common.models.site import ScrapeMethodConfiguration
from backend.scrapeworker.common.selectors import filter_by_hidden_value, filter_by_href


class PlaywrightWordPressAjaxStrategy:

    config: ScrapeMethodConfiguration
    driver: PlaywrightWordPressAjax
    selectors: list[str]

    def __init__(
        self, config: ScrapeMethodConfiguration, driver: PlaywrightWordPressAjax
    ):
        self.config = config
        self.driver = driver
        self.selectors = []

    @cached_property
    def css_selector(self) -> str:

        href_selectors = filter_by_href(javascript=True)
        return ", ".join(href_selectors)

    async def execute(self, url):

        await self.driver.nav_to_page(url)

        # elements = await self.driver.find_elements('a:not([href])[target="_blank"]')
        elements = await self.driver.find_elements("a.nav-link")
        logging.info(f"elementsLength={len(elements)}")

        downloads = await self.driver.collect_downloads(elements)
        logging.info(f"downloadsLength={len(downloads)}")

        return (elements, downloads)
