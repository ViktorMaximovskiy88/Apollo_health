from typing import Callable
from urllib.parse import ParseResult, urlparse

from playwright.async_api import ElementHandle, Locator

from backend.common.models.site import ScrapeMethodConfiguration
from backend.scrapeworker.common.models import DownloadContext, Metadata, Request
from backend.scrapeworker.common.utils import normalize_url
from backend.scrapeworker.scrapers.direct_download import DirectDownloadScraper


class AetnaMedicareScraper(DirectDownloadScraper):
    type: str = "AetnaMedicareScraper"
    is_batchable: bool = True
    batch_size: int = 5
    skip_hash_check: bool = True

    state_selector = (
        "#content_section_findadrug_drugComponentContainerLeft_xmlfilter_filtergroup-state"
    )
    county_selector = (
        "#content_section_findadrug_drugComponentContainerLeft_xmlfilter_filtergroup-county"
    )
    plan_selector = (
        "#content_section_findadrug_drugComponentContainerLeft_xmlfilter_filtergroup-plan-name"
    )

    @staticmethod
    def scrape_select(url, config: ScrapeMethodConfiguration | None = None) -> bool:
        parsed_url: ParseResult = urlparse(url)
        path_match = "/en/prescription-drugs/check-medicare-drug-list.html"
        result = parsed_url.netloc == "www.aetnamedicare.com" and parsed_url.path == path_match
        return result

    async def execute_batches(self):
        # this sections adds to SessionStorage: {"findadrug":{"openComponent":true}}
        # the click(selector) wasnt as dependable
        button = await self.page.query_selector(".getDrugInfoBtn")
        await button.click()

        # TODO get fancy
        state_values = await self.get_state_options()
        for state_value in state_values:
            await self.page.select_option(self.state_selector, state_value)
            county_values = await self.get_county_options()
            for county_value in county_values:
                await self.page.select_option(self.county_selector, county_value)
                plan_values = await self.get_plan_name_options()
                for plan_value in plan_values:
                    await self.select_plan(plan_value)
                    plan_downloads = await self.get_downloads()
                    yield plan_downloads

    async def get_downloads(self):
        base_tag_href = await self.get_base_href()
        base_url = self.page.url
        cookies = await self.context.cookies(base_url)

        link_locator: Locator = self.page.locator('.xmlfilter__result a[href$=".pdf"]')
        link_handles = await link_locator.element_handles()

        downloads = []
        for link_handle in link_handles:
            metadata: Metadata = await self.extract_metadata(link_handle, "href")
            url = normalize_url(base_url, metadata.resource_value, base_tag_href)
            metadata.base_url = base_url
            downloads.append(
                DownloadContext(metadata=metadata, request=Request(url=url, cookies=cookies))
            )

        return downloads

    @staticmethod
    def option_request(match: str) -> bool:
        return lambda request: match in request.url

    async def fetch_option_values(self, selector: str, predicate: Callable) -> list[ElementHandle]:
        async with self.page.expect_request_finished(predicate):
            pass

        option_locator: Locator = self.page.locator(f"{selector} option")
        handles = await option_locator.element_handles()
        option_values = []
        for handle in handles:
            value: ElementHandle = await handle.get_attribute("value")
            if value and value not in ["--"]:
                option_values.append(value)
        return option_values

    async def get_state_options(self) -> list[ElementHandle]:
        match_url = "&returnBy=state"
        state_options = await self.fetch_option_values(
            self.state_selector, self.option_request(match_url)
        )
        return state_options

    async def get_county_options(self) -> list[ElementHandle]:
        match_url = "&returnBy=county&filterBy=state"
        county_options = await self.fetch_option_values(
            self.county_selector, self.option_request(match_url)
        )
        return county_options

    async def get_plan_name_options(self) -> list[ElementHandle]:
        match_url = "&returnBy=plan-name&filterBy=state&filterBy=county"  # noqa
        plan_options = await self.fetch_option_values(
            self.plan_selector, self.option_request(match_url)
        )
        return plan_options

    async def select_plan(self, plan: str) -> list[ElementHandle]:
        match_url = (
            "&returnBy=link-name&returnBy=path-filename&filterBy=state&filterBy=county"  # noqa
        )
        async with self.page.expect_request_finished(self.option_request(match_url)):
            await self.page.select_option(self.plan_selector, plan)
