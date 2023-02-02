from aiofiles import tempfile
from playwright.async_api import Request as PlaywrightRequest
from playwright.async_api import Route, TimeoutError

from backend.common.storage.hash import hash_bytes
from backend.scrapeworker.common.models import DownloadContext, Metadata, Request
from backend.scrapeworker.scrapers.direct_download import DirectDownloadScraper


class AetnaScraper(DirectDownloadScraper):
    type: str = "Aetna"
    base_url = "https://www.aetna.com/search/results.aspx?cfg=wwwcpcpbext&query=policy&offset=0&YearSelect=2023&years=2022-2023"  # noqa

    @staticmethod
    def page_route(route: Route, request: PlaywrightRequest):
        if (
            request.url == "https://www.aetna.com/pon-your-euer-King-O-hoa-Measurall-I-my-Leason-t"
            or request.url.startswith("https://www.aetna.com/_Incapsula_Resource?")
        ):
            return route.abort()
        else:
            return route.continue_()

    async def parse_urls(self, urls: list[str]):
        downloads: list[DownloadContext] = []
        for url in urls:
            cleaned_url = url.strip()
            try:
                response = await self.page.goto(cleaned_url)
            except TimeoutError:
                self.log.debug(f"Playwright timeout error when scraping {cleaned_url}")
                continue
            if not response or not response.ok:
                self.log.debug(f"None or bad response from {cleaned_url}.")
                continue
            html_text = await response.text()
            body = bytes(html_text.strip(), "utf-8")
            file_hash = hash_bytes(body)
            title = await self.page.title()
            async with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as file:
                await file.write(body)
                temp_path = file.name

            downloads.append(
                DownloadContext(
                    file_path=temp_path,
                    file_name=title,
                    file_extension="html",
                    playwright_download=True,
                    file_hash=file_hash,
                    metadata=Metadata(
                        link_text=title,
                        base_url=self.page.url,
                    ),
                    request=Request(
                        url=f"file://{temp_path}",
                        filename=title,
                    ),
                )
            )
        return downloads

    async def execute(self) -> list[DownloadContext]:
        await self.page.route("**/*", self.page_route)
        downloads: list[DownloadContext] = []
        offset = 0
        while True:
            target_url = f"https://www.aetna.com/search/results.aspx?cfg=wwwcpcpbext&query=policy&offset={offset}&YearSelect=2023&years=2022-2023"  # noqa
            await self.page.wait_for_timeout(1500)
            try:
                await self.page.goto(target_url)
            except TimeoutError:
                self.log.debug(f"Playwright timeout when navigating to {target_url}")
                offset += 10
                continue
            locator = self.page.locator("//Results/Result/ResultField[@Name='url']")
            urls = await locator.all_text_contents()
            if not urls:
                self.log.debug(f"No scrapeable urls found on page {target_url}")
                break
            downloads += await self.parse_urls(urls)
            offset += 10
        return downloads
