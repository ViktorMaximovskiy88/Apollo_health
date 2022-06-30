import logging
import asyncio
from playwright_stealth import stealth_async
from playwright.async_api import (
    Page,
    Locator,
    ElementHandle,
    ProxySettings,
)
from backend.scrapeworker.strategies import base_mixins
from backend.common.core.config import config
from backend.scrapeworker.common.models import Metadata
from backend.common.models.proxy import Proxy


async def nav_to_page(page, url, wait_until="domcontentloaded", timeout=3000):
    await stealth_async(page)
    await page.goto(url, wait_until=wait_until, timeout=timeout)


async def find_elements(page: Page, css_selector: str) -> list[ElementHandle]:
    return await page.query_selector_all(css_selector)


async def watch_elements(page: Page, css_selector: str) -> Locator:
    return await page.locator(css_selector)


async def extract_metadata(element: ElementHandle) -> Metadata:

    closest_heading: str | None

    link_text, element_id, href, closest_heading = await asyncio.gather(
        element.text_content(),
        element.get_attribute("id"),
        element.get_attribute("href"),
        element.evaluate(base_mixins.closest_heading_expression),
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


def convert_proxy(proxy: Proxy):
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
