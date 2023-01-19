import asyncio
import re

from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from backend.scrapeworker.common.models import DownloadContext, Request
from backend.scrapeworker.scrapers.playwright_base_scraper import PlaywrightBaseScraper


class BcbsflScraper(PlaywrightBaseScraper):

    type: str = "Bcbsfl"
    downloads: list[DownloadContext] = []
    base_url = "https://mcgs.bcbsfl.com"

    pdf_src_pattern = re.compile(r"\.aspx?.+")
    first_menu_xpath = '//span[contains(text(), "Current Guidelines")]'
    second_menu_xpath = '//span[contains(text(), "Alphabetical")]'
    doc_options_xpath = (
        '//ul[@class="rpGroup rpLevel2 "]/li[@class="rpItem"]/'
        'a[@class="rpLink "]/span/span[@class="rpText"]'
    )
    iframe_xpath = '//div[@id="divLiteralContainer"]/iframe'

    async def is_applicable(self) -> bool:
        self.log.debug(f"self.parsed_url.netloc={self.parsed_url.netloc}")
        result = self.parsed_url.netloc in ["mcgs.bcbsfl.com"]
        self.log.info(f"{self.__class__.__name__} is_applicable -> {result}")
        return result

    async def click_welcome_menu_elements(self):
        first_menu_path = await self.page.wait_for_selector(self.first_menu_xpath)
        await first_menu_path.click()
        second_menu_xpath = await self.page.wait_for_selector(self.second_menu_xpath)
        await second_menu_xpath.click()

    @staticmethod
    async def intercept(route, request):
        if "FilePath" in request.url:
            await route.abort()
        else:
            await route.continue_()

    async def execute(self) -> list[DownloadContext]:
        downloads: list[DownloadContext] = []
        found_pdfs = []

        await self.page.route("**/*", self.intercept)
        await self.click_welcome_menu_elements()
        xpath_locator = self.page.locator(self.doc_options_xpath)
        all_texts = await xpath_locator.all_inner_texts()
        for text in all_texts:
            try:
                await self.click_welcome_menu_elements()
                await self.click_welcome_menu_elements()
                pdf_el = self.page.locator(self.iframe_xpath)
                pdf_raw_src = await pdf_el.get_attribute("src")
                welcome_pdf_src = self.pdf_src_pattern.findall(str(pdf_raw_src))[0][5:]
                link_handle = await self.page.wait_for_selector(
                    f"//ul[@class='rpGroup rpLevel2 ']"
                    f"/li[@class='rpItem']"
                    f"/a[@class='rpLink ']"
                    f"/span/span[text()='{text}']"
                )
                metadata = await self.extract_metadata(link_handle)
                metadata.base_url = self.base_url
                await link_handle.click()
                await asyncio.sleep(0.25)

                await self.page.wait_for_selector(
                    f'//div[@id="divLiteralContainer"]'
                    f"/iframe[not(contains(@src,"
                    f'"{welcome_pdf_src}"))]',
                )
                await self.page.wait_for_selector(self.iframe_xpath)
                result_pdf_locator = self.page.locator(self.iframe_xpath)
                found_pdfs.append(
                    {
                        "path": await result_pdf_locator.get_attribute("src"),
                        "metadata": metadata,
                    }
                )
            except PlaywrightTimeoutError as e:
                self.log.error(
                    f"TimeoutException in {self.__class__.__name__} class for"
                    f" execute method: {e}"
                )
                await asyncio.sleep(10)

        self.log.info(f"found {len(found_pdfs)} pdfs")

        for pdf in found_pdfs:
            src = pdf["path"]
            downloads.append(
                DownloadContext(
                    request=Request(url=f"{self.base_url}/{src}"),
                    metadata=pdf["metadata"],
                )
            )

        await self.page.unroute("**/*", self.intercept)
        return downloads
