import logging
import asyncio
from urllib.parse import urlparse
from playwright_stealth import stealth_async
from playwright.async_api import (
    BrowserContext,
    Page,
    Locator,
    ElementHandle,
    ProxySettings,
)
from backend.common.core.config import config
from backend.scrapeworker.drivers.base_driver import BaseDriver
from backend.scrapeworker.common.models import Metadata
from backend.common.models.proxy import Proxy


class PlaywrightDriver(BaseDriver):
    context: BrowserContext
    page: Page

    def open_context(self, context: BrowserContext, page: Page):
        self.context = context
        self.page = page

    async def close_context(self):
        await self.context.close()

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

    async def nav_to_page(self, url, wait_until="domcontentloaded"):
        self.url = url
        self.parsed_url = urlparse(url)
        await stealth_async(self.page)
        await self.page.goto(self.url, wait_until=wait_until)

    async def find_elements(self, css_selector: str) -> list[ElementHandle]:
        return await self.page.query_selector_all(css_selector)

    async def watch_elements(self, css_selector: str) -> Locator:
        return await self.page.locator(css_selector)

    async def extract_metadata(self, element: ElementHandle) -> Metadata:

        link_text, element_id, href, closest_heading = await asyncio.gather(
            element.text_content(),
            element.get_attribute("id"),
            element.get_attribute("href"),
            element.evaluate(self.closest_heading_expression),
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
