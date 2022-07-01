from playwright.async_api import Page, BrowserContext
from backend.common.models.site import ScrapeMethodConfiguration
from backend.scrapeworker.strategies import base_mixins


class BaseStrategy:
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
