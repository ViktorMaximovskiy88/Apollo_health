from logging import Logger

from playwright.async_api import Page, TimeoutError

from backend.common.models.search_codes import SearchCodeSet
from backend.common.models.site import ScrapeMethodConfiguration
from backend.scrapeworker.common.selectors import to_xpath
from backend.scrapeworker.playbook import PlaybookContext, ScrapePlaybook


class SearchableCrawler:
    def __init__(self, config: ScrapeMethodConfiguration, log: Logger) -> None:
        self.config = config
        self.input_selector: str | None = (
            to_xpath(config.searchable_input) if config.searchable_input else None
        )
        self.submit_selector: str | None = (
            to_xpath(config.searchable_submit) if config.searchable_submit else None
        )
        self.log = log

    async def __codes(self):
        search_codes = await SearchCodeSet.find_one({"type": self.config.searchable_type})
        if search_codes:
            return search_codes.codes
        return set()

    async def replay_playbook(self, page: Page, playbook_context: PlaybookContext):
        playbook = ScrapePlaybook(playbook_str=None, playbook_context=playbook_context)
        async for step in playbook.run_playbook(page):
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
        try:
            async with page.expect_event("load", timeout=10000):
                try:
                    if self.submit_selector:
                        await page.click(self.submit_selector, timeout=1)
                    else:
                        await page.keyboard.press("Enter")
                except TimeoutError as err:
                    raise err
            return True
        except TimeoutError:
            return False

    async def run_searchable(self, page: Page, playbook_context: PlaybookContext):
        base_url = page.url
        codes = await self.__codes()

        for code in codes:
            has_navigated = False
            try:
                await self.__type(page, code)
                await self.__select(page, code)
                has_navigated = await self.__search(page)
                yield code
            except Exception:
                self.log.error("Searchable Execution Error", exc_info=True)
            if has_navigated:
                await page.goto(base_url)
                await self.replay_playbook(page, playbook_context)
