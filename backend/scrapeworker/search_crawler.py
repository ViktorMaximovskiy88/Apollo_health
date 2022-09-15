import logging

from playwright.async_api import Page

from backend.common.models.search_codes import SearchCodeSet
from backend.common.models.site import ScrapeMethodConfiguration
from backend.scrapeworker.common.selectors import to_xpath
from backend.scrapeworker.playbook import PlaybookContext, ScrapePlaybook


class SearchableCrawler:
    def __init__(self, config: ScrapeMethodConfiguration) -> None:
        self.config = config
        self.input_selector: str | None = (
            to_xpath(config.searchable_input) if config.searchable_input else None
        )
        self.submit_selector: str | None = (
            to_xpath(config.searchable_submit) if config.searchable_submit else None
        )

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

    async def run_searchable(self, page: Page, playbook_context: PlaybookContext):
        assert self.input_selector is not None
        base_url = page.url
        codes = await self.__codes()
        for code in codes:
            try:
                await page.fill(self.input_selector, "")
                await page.fill(self.input_selector, code)
                if self.submit_selector:
                    await page.click(self.submit_selector)
                else:
                    await page.keyboard.press("Enter")
                yield code
            except Exception:
                logging.error("Searchable Execution Error", exc_info=True)
            finally:
                if page.url != base_url:
                    await page.goto(base_url)
                    await self.replay_playbook(page, playbook_context)
