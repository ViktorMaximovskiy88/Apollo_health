from playwright.async_api import Page, BrowserContext, ElementHandle
from backend.common.models.site import ScrapeMethodConfiguration
from backend.scrapeworker.strategies import playwright_mixins
from backend.scrapeworker.strategies import base_mixins


class BaseStrategy:

    config: ScrapeMethodConfiguration
    selectors: list[str]
    url: str

    def __init__(
        self,
        context: BrowserContext,
        page: Page,
        url: str,
        config: ScrapeMethodConfiguration,
    ):
        self.context = context
        self.page = page
        self.config = config
        self.url = url
        self.parsed_url = base_mixins.parse_url(self.url)
        self.selectors = []

    async def nav_to_page(
        self,
        timeout=60000,
    ):
        return await playwright_mixins.nav_to_page(
            self.page,
            self.url,
            timeout=timeout,
        )

    async def find_elements(
        self,
        css_selector,
    ):
        return await playwright_mixins.find_elements(
            self.page,
            css_selector,
        )

    async def extract_metadata(
        self,
        element,
    ):
        return await playwright_mixins.extract_metadata(
            element,
        )
