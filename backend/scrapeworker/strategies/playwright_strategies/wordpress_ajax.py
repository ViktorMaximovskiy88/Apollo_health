import logging
from playwright.async_api import Browser, ProxySettings
from backend.common.models.site import ScrapeMethodConfiguration
from backend.scrapeworker.drivers.playwright_driver import PlaywrightDriver
from backend.common.models.proxy import Proxy


class WordPressAjaxStrategy:

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

    async def session(self, proxy_settings: ProxySettings):
        logging.info("enter session")
        context = await self.browser.new_context(
            ignore_https_errors=True, proxy=proxy_settings
        )
        page = await self.browser.new_page()
        self.driver.open_context(context=context, page=page)

    async def execute(self, url, proxies: list[Proxy]):
        self.proxies = self.driver.convert_proxies(proxies=proxies)

        self.json_docs = []

        async def intercept(route, request):
            if "/wp-admin/admin-ajax.php" in request.url:
                print("intercept continue", request)
                self.json_docs.append(request)
            await route.continue_()

        async for attempt, proxy_settings in self.driver.proxy_with_backoff(
            self.proxies
        ):
            with attempt:
                await self.session(proxy_settings)
                await self.driver.page.route("**/*", intercept)
                await self.driver.nav_to_page(url)

                # need to use jq/jsonpath to look into JSON and get pdfs + metdata
                elements = await self.driver.find_elements("a.nothing")

                logging.info(f"elementsLength={len(elements)}")

                downloads = self.json_docs
                logging.info(f"downloadsLength={len(downloads)}")

                await self.driver.page.unroute("**/*", intercept)
                await self.driver.close_context()

                return (elements, downloads)
