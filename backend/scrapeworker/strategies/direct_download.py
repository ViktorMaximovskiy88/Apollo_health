import logging
from functools import cached_property
from backend.scrapeworker.drivers.base_driver import BaseDriver
from backend.common.models.site import ScrapeMethodConfiguration
from backend.scrapeworker.common.selectors import filter_by_hidden_value, filter_by_href


class DirectDownloadStategy:

    config: ScrapeMethodConfiguration
    driver: BaseDriver
    selectors: list[str]

    def __init__(self, config: ScrapeMethodConfiguration, driver: BaseDriver):
        self.config = config
        self.driver = driver
        self.selectors = []

    @cached_property
    def css_selector(self) -> str:

        href_selectors = filter_by_href(
            extensions=self.config.document_extensions,
            keywords=self.config.url_keywords,
        )

        hidden_value_selectors = filter_by_hidden_value(
            extensions=self.config.document_extensions,
            keywords=self.config.url_keywords,
        )

        self.selectors = self.selectors + href_selectors + hidden_value_selectors

        return ", ".join(self.selectors)

    async def execute(self, url):

        await self.driver.nav_to_page(url)

        elements = await self.driver.find_elements(self.css_selector)
        logging.info(f"elementsLength={len(elements)}")

        downloads = await self.driver.collect_downloads(elements)
        logging.info(f"downloadsLength={len(downloads)}")

        return (elements, downloads)
