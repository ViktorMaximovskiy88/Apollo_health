import asyncio
import logging
from abc import ABC, abstractmethod
from functools import cached_property
from typing import AsyncGenerator, Callable
from urllib.parse import urlparse, urlsplit

from playwright.async_api import (
    BrowserContext,
    ElementHandle,
    Error,
    Page,
    ProxySettings,
    Request,
    Route,
    TimeoutError,
)

from backend.common.core.config import config
from backend.common.core.enums import ScrapeMethod
from backend.common.models.proxy import Proxy
from backend.common.models.site import ScrapeMethodConfiguration
from backend.scrapeworker.common.models import DownloadContext, Metadata
from backend.scrapeworker.playbook import PlaybookContext, ScrapePlaybook

is_maybe_modal: str = """
    (node) => {
        const zIndex = parseInt(getComputedStyle(node).zIndex);
        return !isNaN(zIndex) && zIndex > 10;
    }
"""

closest_heading_expression: str = """
    (node) => {
        let n = node;
        while (n) {
            const h = n.querySelector('h1, h2, h3, h4, h5, h6, label')
            if (h) return h.textContent;
            n = n.parentNode;
        }
        return '';
    }
"""


sibling_text_expression: str = """
    (node) => {
        let n = node;
        while (n) {
            if(n.tagName == 'TD' && n.previousElementSibling) {
                return n.previousElementSibling.textContent
            }
            n = n.parentNode;
        }
        return '';
    }
"""


class PlaywrightBaseScraper(ABC):
    base_url: str = None
    is_batchable = False
    batch_size = 20
    page_route: Callable | None = None

    def __init__(
        self,
        context: BrowserContext,
        page: Page,
        url: str,
        config: ScrapeMethodConfiguration,
        scrape_method: ScrapeMethod | None = None,
        log: logging.Logger = logging.getLogger(__name__),
        playbook_context: PlaybookContext = [],
        metadata: dict = {},
    ):
        self.context = context
        self.page = page
        self.config = config
        self.url = url
        self.playbook_context = playbook_context
        self.parsed_url = urlparse(self.url)
        self.selectors = []
        self.log = log
        self.metadata = metadata
        self.scrape_method = scrape_method

    @cached_property
    def css_selector(self) -> str | None:
        return None

    @cached_property
    def xpath_selector(self) -> str | None:
        return None

    @staticmethod
    def scrape_select(url, config: ScrapeMethodConfiguration | None = None) -> bool:
        raise NotImplementedError("scrape_select is not implemented on this scraper")

    async def _fetch(
        self,
        url,
        method: str = "GET",
        headers: dict | None = None,
        data: dict | None = None,
        params: dict | None = None,
    ):
        try:
            response = await self.page.request.fetch(
                url,
                method=method,
                data=data,
                params=params,
                headers=headers,
                fail_on_status_code=True,
            )

            result = await response.body()
            await response.dispose()
            return result

        except TimeoutError as ex:
            self.log.error(f"data={data}", exc_info=ex)
        except Error as ex:
            self.log.error(f"data={data}", exc_info=ex)
        except Exception as ex:
            self.log.error(f"data={data}", exc_info=ex)

    async def find_in_page(self, page: Page) -> bool:
        css_handle = None
        if self.css_selector:
            css_handle = await page.query_selector(self.css_selector)

        xpath_locator_count = 0
        if self.xpath_selector:
            xpath_locator = page.locator(self.xpath_selector)
            xpath_locator_count = await xpath_locator.count()

        return css_handle is not None or xpath_locator_count > 0

    async def dismiss_modals(self):

        if self.config.prompt_button_selector:
            button = await self.page.query_selector(self.config.prompt_button_selector)
            if button:
                await button.click()
        else:
            modal_handles = await self.page.query_selector_all("div:visible")

            for modal_handle in modal_handles:
                maybe_modal = await modal_handle.evaluate(is_maybe_modal)
                if maybe_modal:
                    button = await modal_handle.query_selector(
                        'button:text-matches("(yes|agree|continue|accept|ok)", "i")'
                    )
                    if button:
                        await button.click()

    async def is_applicable(self) -> bool:

        timeout = self.config.wait_for_timeout_ms
        await self.page.wait_for_timeout(timeout)

        await self.dismiss_modals()

        in_parent_frame = await self.find_in_page(self.page)

        in_child_frame = False
        if len(self.page.main_frame.child_frames) > 0 and self.config.search_in_frames:
            child_frames = self.page.main_frame.child_frames
            in_child_frame = await self.find_in_page(child_frames[0].page)

        result = in_parent_frame or in_child_frame
        self.log.info(f"{self.__class__.__name__} is_applicable -> {result}")
        return result

    async def get_base_href(self) -> str | None:
        base_tag = await self.page.query_selector("head base")
        if base_tag:
            return await base_tag.get_attribute("href")
        return None

    async def extract_metadata(
        self, element: ElementHandle, resource_attr: str = "href"
    ) -> Metadata:

        closest_heading: str | None
        (
            element_content,
            element_text,
            element_id,
            resource_value,
            closest_heading,
            siblings_text,
            anchor_target,
        ) = await asyncio.gather(
            element.text_content(),
            element.inner_text(),
            element.get_attribute("id"),
            element.get_attribute(resource_attr),
            element.evaluate(closest_heading_expression),
            element.evaluate(sibling_text_expression),
            element.get_attribute("target"),
        )

        if isinstance(siblings_text, str):
            siblings_text = siblings_text.strip() or None

        # Use first response for inner_text() text_content() for link_text.
        # If an element has no text (<p></p>), use url path.
        if element_content and element_content.strip():
            link_text = element_content.strip()
        elif element_text and element_text.strip():
            link_text = element_text.strip()
        elif siblings_text:
            link_text = siblings_text
        elif resource_value and resource_value.strip():
            parsed_url = urlsplit(resource_value)
            link_text = parsed_url.path
        else:
            link_text = self.parsed_url.path

        if closest_heading:
            closest_heading = closest_heading.strip()

        return Metadata(
            link_text=link_text,
            element_id=element_id,
            resource_value=resource_value,
            closest_heading=closest_heading,
            playbook_context=self.playbook_context,
            siblings_text=siblings_text,
            anchor_target=anchor_target,
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

    async def replay_playbook(self):
        playbook = ScrapePlaybook(playbook_str=None, playbook_context=self.playbook_context)
        async for _ in playbook.run_playbook(self.page):
            continue

    async def nav_to_base(self):
        try:
            await self.page.goto(self.url)
            await self.replay_playbook()
        except Exception as ex:
            self.log.error(ex, exc_info=True, stack_info=True)

    async def execute_batches(self) -> AsyncGenerator[list[DownloadContext], None]:
        downloads: list[DownloadContext] = []
        yield downloads

    @abstractmethod
    async def execute(self) -> list[DownloadContext]:
        pass

    @staticmethod
    async def page_route(route: Route, request: Request):
        await route.continue_()
