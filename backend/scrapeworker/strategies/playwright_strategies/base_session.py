import logging
from playwright.async_api import ProxySettings, Browser


class PlaywrightSession:
    def __init__(
        self,
        browser: Browser,
        proxy_settings: ProxySettings,
    ):
        self.browser = browser
        self.proxy_settings = proxy_settings

    async def __aenter__(self):
        logging.info("enter playwright session")
        self.context = await self.browser.new_context(
            ignore_https_errors=True, proxy=self.proxy_settings
        )
        self.page = await self.browser.new_page()
        return self

    async def __aexit__(self, *exc):
        logging.info("enter playwright session")
        await self.context.close()
