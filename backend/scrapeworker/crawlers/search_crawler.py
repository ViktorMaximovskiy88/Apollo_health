from dataclasses import dataclass
from logging import Logger

from playwright.async_api import Locator, Page

from backend.common.models.search_codes import SearchCodeSet
from backend.common.models.site import ScrapeMethodConfiguration
from backend.scrapeworker.common.selectors import to_xpath
from backend.scrapeworker.playbook import PlaybookContext, ScrapePlaybook


@dataclass
class NavState:
    has_navigated: bool = False

    def handle_nav(self, _):
        self.has_navigated = True


class SearchableCrawler:
    inside_a_tag_expression: str = """
        (node) => {
            let n = node;
            while (n) {
                let current_node_type = n.tagName;
                if (current_node_type === "A") {
                    return true
                }
                n = n.parentNode;
            }
            return false;
        }
    """

    def __init__(self, config: ScrapeMethodConfiguration, log: Logger) -> None:
        self.config = config
        self.input_selector: str | None = (
            to_xpath(config.searchable_input) if config.searchable_input else None
        )
        self.submit_selector: str | None = (
            to_xpath(config.searchable_submit)
            if config.searchable_submit and config.searchable_submit.attr_element
            else None
        )
        self.log = log
        self.searchable_playbook = ScrapePlaybook(config.searchable_playbook)

    def _get_prefix_codes(self, search_codes: list[str], prefix_length: int) -> list[str]:
        prefix_codes: set[str] = set()
        for term in search_codes:
            prefix_code = term[:prefix_length].lower()
            prefix_codes.add(prefix_code)
        prefix_codes_list = list(prefix_codes)
        prefix_codes_list.sort()
        return prefix_codes_list

    async def __codes(self) -> list[str]:
        search_codes_list: list[str] = []
        for search_code in self.config.searchable_type:
            search_codes = await SearchCodeSet.find_one({"type": search_code})
            if search_codes:
                search_codes_list += list(search_codes.codes)

        if self.config.search_prefix_length:
            return self._get_prefix_codes(search_codes_list, self.config.search_prefix_length)
        return search_codes_list

    async def __resolve_selector(self, page: Page) -> Locator:
        if self.input_selector is None:
            raise Exception("Input selector must be given.")
        input_locators = page.locator(self.input_selector)
        if await input_locators.count() == 1:
            return input_locators
        for locator in await input_locators.all():
            if await locator.is_visible():
                return locator
        raise Exception("No visible locators found.")

    async def replay_playbook(self, page: Page, playbook_context: PlaybookContext):
        playbook = ScrapePlaybook(playbook_str=None, playbook_context=playbook_context)
        async for _ in playbook.run_playbook(page):
            continue

    async def run_searchable_playbook(self, page: Page):
        searchable_playbook = self.searchable_playbook
        async for _ in searchable_playbook.run_playbook(page):
            continue

    async def is_searchable(self, page: Page):
        timeout = self.config.wait_for_timeout_ms
        await page.wait_for_timeout(timeout)
        locator_count = 0
        if self.config.searchable and self.input_selector:
            locators = page.locator(self.input_selector)
            locator_count = await locators.count()

        return locator_count > 0

    async def __type(self, page: Page, code: str):
        input_locator = await self.__resolve_selector(page)
        await input_locator.fill("")
        await input_locator.fill(code)

    async def __select(self, page: Page, code: str):
        """
        Best attempt to check for and click the appropriate option.
        """
        try:
            select_locator = page.locator(":not(input)", has_text=code).last
            if await select_locator.count() == 0:
                return
            in_anchor_tag = await select_locator.evaluate(self.inside_a_tag_expression)
            if in_anchor_tag:
                return
            await select_locator.click(timeout=5000)
        except Exception:
            return

    async def __search(self, page: Page):
        if self.submit_selector:
            await page.click(self.submit_selector)
        else:
            await page.keyboard.press("Enter")

    async def run_searchable(self, page: Page, playbook_context: PlaybookContext):
        base_url = page.url
        codes = await self.__codes()
        for code in codes:
            nav_state = NavState()
            try:
                page.on("load", nav_state.handle_nav)
                # runs searchable playbook if provided from collection settings
                await self.run_searchable_playbook(page)
                await self.__type(page, code)
                await self.__select(page, code)
                await self.__search(page)
                yield code
            except Exception as e:
                self.log.error(f"Searchable Execution Error: {e}", exc_info=e)
            if nav_state.has_navigated or page.url != base_url:
                await page.goto(base_url)
                await self.replay_playbook(page, playbook_context)
