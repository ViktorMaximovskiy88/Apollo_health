import asyncio
from abc import ABC, abstractmethod
from functools import cached_property
from urllib.parse import urlparse

from playwright.async_api import BrowserContext, ElementHandle, Page, ProxySettings

from backend.common.core.config import config
from backend.common.models.proxy import Proxy
from backend.common.models.site import ScrapeMethodConfiguration
from backend.scrapeworker.common.models import DownloadContext, Metadata
from backend.scrapeworker.playbook import PlaybookContext

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
        playbook_context: PlaybookContext = [],
    ):
        self.context = context
        self.page = page
        self.config = config
        self.url = url
        self.playbook_context = playbook_context
        self.parsed_url = urlparse(self.url)
        self.selectors = []

    @cached_property
    def css_selector(self) -> str:
        raise NotImplementedError("css_selector is required ")

    async def is_applicable(self) -> bool:
        await self.page.wait_for_timeout(2000)

        element_handle = await self.page.query_selector(self.css_selector)
        if element_handle is not None:
            return True

        child_frames = self.page.main_frame.child_frames

        if len(child_frames) > 0:
            element_handle = await child_frames[0].query_selector(self.css_selector)
            return element_handle is not None

        return False

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
            playbook_context=self.playbook_context,
        )

    def convert_proxy(self, proxy: Proxy):
        username: str | None = None
        password: str | None = None
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

    @abstractmethod
    async def execute(self) -> list[DownloadContext]:
        pass
