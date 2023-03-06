from typing import AsyncGenerator
from urllib.parse import ParseResult, urlparse

from aiofiles import tempfile
from playwright.async_api import Page, TimeoutError

from backend.common.models.site import ScrapeMethodConfiguration
from backend.common.storage.hash import hash_bytes
from backend.scrapeworker.common.models import DownloadContext, Request
from backend.scrapeworker.crawlers.search_crawler import SearchableCrawler
from backend.scrapeworker.scrapers.direct_download import DirectDownloadScraper


class Compliance360(DirectDownloadScraper):
    type: str = "Compliance360"
    is_batchable: bool = True
    batch_size: int = 20

    @staticmethod
    def scrape_select(url, config: ScrapeMethodConfiguration | None = None) -> bool:
        parsed_url: ParseResult = urlparse(url)
        parsed_url = urlparse(url)
        return parsed_url.netloc == "secure.compliance360.com"

    async def paginate(self) -> AsyncGenerator[Page, None]:
        pagination_target = "#NavNext:not(.disabled)"
        target = self.page.locator(pagination_target)
        max_iter = 150
        count = 0
        while await target.count() > 0 and count < max_iter:
            count += 1
            try:
                await target.first.click(timeout=5000)
            except TimeoutError:
                break
            yield self.page
            target = self.page.locator(pagination_target)

    async def fetch_pdfs(self, page: Page) -> list[DownloadContext]:
        download_queue: list[DownloadContext] = []
        if not await self.is_applicable():
            return download_queue

        await self.scrape_and_queue(download_queue, page)
        downloads: list[DownloadContext] = []
        for download in download_queue:
            url = download.request.url
            self.log.info(f"before fetch request.url={url}")
            pdf_bytes = await self._fetch(url)
            if not pdf_bytes:
                continue
            self.log.info(f"after fetch request.url={url} {len(pdf_bytes)}")
            file_hash = hash_bytes(pdf_bytes)
            async with tempfile.NamedTemporaryFile(delete=False) as file:
                await file.write(pdf_bytes)
                temp_path = str(file.name)

            downloads.append(
                DownloadContext(
                    file_path=temp_path,
                    file_name=download.metadata.link_text,
                    playwright_download=True,
                    file_hash=file_hash,
                    metadata=download.metadata,
                    request=Request(
                        url=f"file://{temp_path}",
                        filename=download.metadata.link_text,
                    ),
                )
            )
        return downloads

    async def execute_batches(self):
        search_crawler = SearchableCrawler(self.config, self.log)
        await self.page.wait_for_timeout(self.config.wait_for_timeout_ms)
        async for _ in search_crawler.run_searchable(self.page, playbook_context=[]):
            yield await self.fetch_pdfs(self.page)
            async for page in self.paginate():
                yield await self.fetch_pdfs(page)
