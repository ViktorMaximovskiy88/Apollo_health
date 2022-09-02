from playwright.async_api import Page

from backend.common.models.site import ScrapeMethodConfiguration


class Searchable:
    def __init__(self, config: ScrapeMethodConfiguration) -> None:
        self.config = config
        self.codes: list[str] = self.__get_values()
        # create selector from attr selector
        self.input_selector: str | None = '//input[contains(@*[contains(name(), "id")], "Code")]'
        # create selector from attr selector
        self.submit_selector: str | None = '//a[contains(@*[contains(name(), "onclick")], "getResults") and contains(text(), "Lookup")]'  # noqa

    def __get_values(self):
        # get values from db by self.config.searchable_type
        codes: list[str] = ["66030", "81120", "81121", "81415", "81416"]
        return codes

    async def is_searchable(self, page: Page):
        locator_count = 0
        if self.config.searchable and self.input_selector:
            locators = page.locator(self.input_selector)
            locator_count = await locators.count()

        return locator_count > 0

    async def run_searchable(self, page: Page):
        # error handling
        assert isinstance(self.input_selector, str)
        for code in self.codes:
            await page.fill(self.input_selector, "")
            await page.fill(self.input_selector, code)
            if self.submit_selector:
                await page.click(self.submit_selector)
            else:
                await page.keyboard.press("Enter")
            yield code
