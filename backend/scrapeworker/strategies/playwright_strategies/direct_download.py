import logging
from urllib.parse import urljoin
from functools import cached_property
from playwright.async_api import Browser, ProxySettings, ElementHandle
from backend.common.models.site import ScrapeMethodConfiguration
from backend.common.models.proxy import Proxy
from backend.scrapeworker.drivers.playwright_driver import PlaywrightDriver
from backend.scrapeworker.common.selectors import filter_by_hidden_value, filter_by_href
from backend.scrapeworker.common.models import Download, Request


class DirectDownloadStategy:

    config: ScrapeMethodConfiguration
    driver: PlaywrightDriver
    selectors: list[str]

    def __init__(
        self,
        browser: Browser,
        config: ScrapeMethodConfiguration,
    ):
        self.browser = browser
        self.config = config
        self.selectors = []
        self.driver = PlaywrightDriver()

    async def session(self, proxy_config: ProxySettings | None):
        logging.info("enter session")
        context = await self.browser.new_context(
            ignore_https_errors=True, proxy=proxy_config
        )
        page = await self.browser.new_page()
        self.driver.open_context(context=context, page=page)

    async def close(self):
        logging.info("close session")
        await self.driver.close_context()

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

    async def collect_downloads(self, elements: list[ElementHandle]) -> list[Download]:
        downloads = []

        el: ElementHandle
        for el in elements:
            metadata = await self.driver.extract_metadata(el)
            downloads.append(
                Download(
                    metadata=metadata,
                    request=Request(
                        method="GET",
                        url=urljoin(self.driver.url, metadata.href),
                    ),
                )
            )

        return downloads

    async def execute(self, url, proxies: list[Proxy]):
        self.proxies = self.driver.convert_proxies(proxies=proxies)
        async for attempt, proxy_config in self.driver.proxy_with_backoff(self.proxies):
            with attempt:

                try:
                    await self.session(proxy_config)

                    await self.driver.nav_to_page(url)
                    logging.info(f"nav_to_page={url}")

                    elements = await self.driver.find_elements(self.css_selector)
                    logging.info(f"elementsLength={len(elements)}")

                    downloads = await self.collect_downloads(elements)
                    logging.info(f"downloadsLength={len(downloads)}")

                    await self.close()

                    return (elements, downloads)
                except Exception as ex:
                    logging.error(ex)
