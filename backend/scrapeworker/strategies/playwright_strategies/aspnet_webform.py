from curses import meta
import logging
from functools import cached_property
from urllib.parse import urlparse, urljoin
from playwright_stealth import stealth_async
from playwright.async_api import (
    Browser,
    ProxySettings,
    ElementHandle,
    Route,
    Request as RouteRequest,
)
from backend.common.models.site import ScrapeMethodConfiguration
from backend.common.models.proxy import Proxy
from backend.scrapeworker.drivers.playwright_driver import PlaywrightDriver
from backend.scrapeworker.common.selectors import filter_by_href
from backend.scrapeworker.common.models import Download, Metadata, Request


class AspNetWebFormStrategy:

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

    @cached_property
    def css_selector(self) -> str:
        href_selectors = filter_by_href(webform=True)
        return ", ".join(href_selectors)

    async def nav_to_page(self, url):
        self.url = url
        parsed_url = urlparse(self.url)

        cookie = {
            "name": "AspxAutoDetectCookieSupport",
            "value": "1",
            "domain": parsed_url.hostname,
            "path": "/",
            "httpOnly": True,
            "secure": True,
        }

        await stealth_async(self.driver.page)
        await self.driver.context.add_cookies([cookie])
        await self.driver.page.goto(
            self.url, wait_until="domcontentloaded", timeout=60000
        )

    async def collect_downloads(self, elements: list[ElementHandle]) -> list[Download]:
        requests: list[Request] = []
        metadatas: list[Metadata] = []
        downloads: list[Download] = []

        async def intercept(route: Route, request: RouteRequest):
            if self.url in request.url and request.method == "POST":
                logging.info(f"intercepted={request.url}")
                requests.append(
                    Request(
                        method=request.method,
                        url=request.url,
                        headers=request.headers,
                        data=request.post_data,
                    )
                )

            await route.continue_()

        await self.driver.page.route("**/*", intercept)

        el: ElementHandle
        for el in elements:
            metadata = await self.driver.extract_metadata(el)
            metadatas.append(metadata)
            await el.click(timeout=3000)

        await self.driver.page.unroute("**/*", intercept)

        request: RouteRequest
        for index, request in enumerate(requests):
            if request:
                downloads.append(
                    Download(
                        metadata=metadata[index],
                        request=request,
                    )
                )

        return downloads

    # maybe anohter way with our proxy converter.. but this isnt the worst
    async def execute(self, url, proxies: list[Proxy]):
        self.proxies = self.driver.convert_proxies(proxies=proxies)
        self.retry_exclusions = []
        async for attempt, proxy_settings in self.driver.proxy_with_backoff(
            self.proxies
        ):
            with attempt:
                # yield attempt, proxy_settings
                await self.session(proxy_settings)

                await self.nav_to_page(url)

                elements = await self.driver.find_elements(self.css_selector)
                logging.info(f"elementsLength={len(elements)}")

                downloads = await self.collect_downloads(elements)
                logging.info(f"downloadsLength={len(downloads)}")

                await self.driver.close_context()

                return (elements, downloads)
