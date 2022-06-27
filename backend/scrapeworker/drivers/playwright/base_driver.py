import logging
from backend.scrapeworker.drivers.base_driver import BaseDriver
from backend.common.models.proxy import Proxy
from playwright.async_api import BrowserContext, Browser, Page, ProxySettings

class PlaywrightDriver(BaseDriver):
    
    browser: Browser
    context: BrowserContext
    page: Page
    proxy: ProxySettings

    def __init__(self, browser: Browser, proxy: Proxy | None):
        self.browser = browser
        self.proxy = proxy
        self.proxy_settings = self.__cast_proxy(proxy)
        
    async def __aenter__(self):
        logging.info('enter context')
        self.context = await self.browser.new_context(proxy=self.proxy, ignore_https_errors=True)
        self.page = await self.browser.new_page()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        logging.info('exit context')
        await self.close()
        
    def __cast_proxy(self, proxy: Proxy) -> ProxySettings:
        pass
    
    async def close(self):
        await self.page.close()
        await self.context.close()
        
    async def find(self, selectors: str):
        return await self.page.query_selector_all(selectors)
