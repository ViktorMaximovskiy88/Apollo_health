import logging
import asyncio
from playwright.async_api import BrowserContext, Browser, Page, ProxySettings
from playwright.async_api import ElementHandle
from backend.scrapeworker.drivers.base_driver import BaseDriver
from backend.common.models.proxy import Proxy
from backend.scrapeworker.common.models import Metadata

class PlaywrightDriver(BaseDriver):
    
    browser: Browser
    context: BrowserContext
    page: Page
    proxy: ProxySettings

    def __init__(self, browser: Browser, proxy: Proxy | None):
        self.browser = browser
        self.proxy = proxy
        self.proxy_settings = None
        
    async def __aenter__(self):
        logging.info('enter context')
        self.context = await self.browser.new_context(proxy=self.proxy, ignore_https_errors=True)
        self.page = await self.browser.new_page()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        logging.info('exit context')
        await self.close()
    
    async def close(self):
        await self.page.close()
        await self.context.close()
        
    async def find_elements(self, css_selector: str) -> list[ElementHandle]:
        print(css_selector)
        return await self.page.query_selector_all(css_selector)
        
    async def extract_metadata(
        self, element: ElementHandle
    ) -> Metadata:
        
        link_text, element_id, href, closest_heading = await asyncio.gather(
            element.text_content(),
            element.get_attribute('id'),
            element.get_attribute('href'),
            element.evaluate(self.closest_heading_expression)
        )
        
        if link_text:
            link_text = link_text.strip()

        if closest_heading:
            closest_heading = closest_heading.strip()
        
        return Metadata(
            link_text=link_text,
            element_id=element_id,
            href=href,
            closest_heading=closest_heading
        )