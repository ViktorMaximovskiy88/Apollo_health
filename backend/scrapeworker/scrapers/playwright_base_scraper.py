import asyncio
import logging
from functools import cached_property
from playwright.async_api import ElementHandle, ProxySettings, BrowserContext, Page
from backend.common.core.config import config
from backend.scrapeworker.common.models import Metadata
from backend.common.models.proxy import Proxy
from backend.common.models.site import ScrapeMethodConfiguration
from urllib.parse import urlparse
from abc import ABC

closest_heading_expression: str = """
    (node) => {
        let n = node;
        while (n) {
            const h = n.querySelector('h1, h2, h3, h4, h5, h6, label')
            if (h) return h.textContent;
            n = n.parentNode;
        }
    }
"""


class PlaywrightBaseScraper(ABC):
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
        self.parsed_url = urlparse(self.url)
        self.selectors = []

    @cached_property
    def css_selector(self) -> str:
        raise NotImplementedError("css_selector is required ")

    async def is_applicable(self) -> bool:
        element_handle: ElementHandle = await self.page.query_selector(
            self.css_selector
        )
        result = element_handle is not None
        logging.info(f"{self.__class__.__name__} is_applicable -> {result}")
        return result

    async def extract_metadata(self, element: ElementHandle) -> Metadata:

        closest_heading: str | None

        link_text, element_id, href, closest_heading = await asyncio.gather(
            element.text_content(),
            element.get_attribute("id"),
            element.get_attribute("href"),
            element.evaluate(closest_heading_expression),
        )

        if link_text:
            link_text = link_text.strip()

        if closest_heading:
            closest_heading = closest_heading.strip()

        return Metadata(
            link_text=link_text,
            element_id=element_id,
            href=href,
            closest_heading=closest_heading,
        )

    def convert_proxy(self, proxy: Proxy):
        username: str | None
        password: str | None
        proxies = []

        if proxy.credentials:
            username = config.get(proxy.credentials.username_env_var, None)
            password = config.get(proxy.credentials.password_env_var, None)

        for endpoint in proxy.endpoints:
            proxies.append(
                ProxySettings(
                    server=endpoint,
                    username=username,
                    password=password,
                )
            )

        return [proxy, proxies]

    async def execute(self):
        pass
