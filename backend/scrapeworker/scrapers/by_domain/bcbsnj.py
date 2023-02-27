from backend.scrapeworker.common.models import DownloadContext, Metadata, Request
from backend.scrapeworker.scrapers.playwright_base_scraper import PlaywrightBaseScraper


class BcbsnjScraper(PlaywrightBaseScraper):

    type: str = "Bcbsnj"
    middle_frame = "frame[name='Middle']"
    bottom_frame = "frame[name='Bottom']"
    alphabetical_menu_selector = "area#HotspotRectangle54_1"

    async def is_applicable(self) -> bool:
        self.log.debug(f"self.parsed_url.netloc={self.parsed_url.netloc}")
        result = self.parsed_url.netloc in ["services3.horizon-bcbsnj.com"]
        self.log.info(f"{self.__class__.__name__} is_applicable -> {result}")
        return result

    async def click_menu_section(self):
        first_menu_el = self.page.frame_locator(self.middle_frame)
        first_menu = first_menu_el.locator(self.alphabetical_menu_selector)
        element = await first_menu.element_handle()
        await element.dispatch_event("click")
        await self.page.wait_for_timeout(5000)

    async def execute(self) -> list[DownloadContext]:
        downloads: list[DownloadContext] = []

        await self.click_menu_section()
        first_menu_el = self.page.frame_locator(self.bottom_frame)
        links = first_menu_el.locator("td > a")
        for element in await links.element_handles():
            metadata: Metadata = await self.extract_metadata(element)
            metadata.base_url = self.page.url
            name: str = await element.get_attribute("href")
            url = f"https://services3.horizon-bcbsnj.com/ddn/NJhealthWeb.nsf/{name}"
            downloads.append(DownloadContext(metadata=metadata, request=Request(url=url)))

        return downloads
