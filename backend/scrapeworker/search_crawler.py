from dataclasses import dataclass
from logging import Logger

from playwright.async_api import Page

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

    async def __codes(self):
        search_codes_list = []
        for search_code in self.config.searchable_type:
            search_codes = await SearchCodeSet.find_one({"type": search_code})
            if search_codes:
                search_codes_list += list(search_codes.codes)

        if search_codes_list:
            return search_codes_list
        return set()

    async def replay_playbook(self, page: Page, playbook_context: PlaybookContext):
        playbook = ScrapePlaybook(playbook_str=None, playbook_context=playbook_context)
        async for _ in playbook.run_playbook(page):
            continue

    async def run_searchable_playbook(self, page: Page):
        searchable_playbook = self.searchable_playbook
        async for _ in searchable_playbook.run_playbook(page):
            continue

    async def is_searchable(self, page: Page):
        locator_count = 0
        if self.config.searchable and self.input_selector:
            locators = page.locator(self.input_selector)
            locator_count = await locators.count()

        return locator_count > 0

    async def __type(self, page: Page, code: str):
        assert self.input_selector is not None
        await page.fill(self.input_selector, "")
        await page.fill(self.input_selector, code)

    async def __select(self, page: Page, code: str):
        """
        Best attempt to check for and click the appropriate option.
        """
        try:
            select_locator = page.locator(":not(input)", has_text=code).last
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
            except Exception:
                self.log.error("Searchable Execution Error", exc_info=True)

            if nav_state.has_navigated or page.url != base_url:
                await page.goto(base_url)
                await self.replay_playbook(page, playbook_context)
