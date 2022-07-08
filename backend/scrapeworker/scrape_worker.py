import asyncio
import logging
import re
from contextlib import asynccontextmanager
from datetime import datetime
from random import shuffle
from typing import AsyncGenerator, Coroutine, Type
from async_lru import alru_cache
from tenacity._asyncio import AsyncRetrying
from tenacity.stop import stop_after_attempt
from beanie.odm.operators.update.array import Push
from beanie.odm.operators.update.general import Inc
from urllib.parse import urlparse
from backend.common.models.proxy import Proxy
from backend.common.models.site import Site
from backend.common.models.document import RetrievedDocument, UpdateRetrievedDocument
from backend.common.models.site_scrape_task import SiteScrapeTask
from playwright.async_api import (
    Browser,
    BrowserContext,
    ProxySettings,
    Page,
)

from playwright_stealth import stealth_async
from backend.common.models.user import User
from backend.scrapeworker.aio_downloader import AioDownloader
from backend.scrapeworker.common.proxy import convert_proxies_to_proxy_settings
from backend.app.utils.logger import Logger, create_and_log, update_and_log_diff
from backend.common.storage.client import DocumentStorageClient
from backend.common.core.enums import Status
from backend.scrapeworker.common.exceptions import (
    NoDocsCollectedException,
    CanceledTaskException,
)
from backend.scrapeworker.common.models import Download
from backend.scrapeworker.scrapers import scrapers
from backend.scrapeworker.scrapers.follow_link import FollowLinkScraper
from backend.scrapeworker.scrapers.playwright_base_scraper import PlaywrightBaseScraper
from backend.scrapeworker.common.proxy import convert_proxies_to_proxy_settings
from backend.app.utils.logger import Logger, create_and_log, update_and_log_diff
from backend.common.storage.client import DocumentStorageClient
from backend.common.core.enums import Status
from backend.scrapeworker.file_parsers import parse_by_type


def is_google(url):
    parsed = urlparse(url)
    return parsed.hostname in ["drive.google.com", "docs.google.com"]


def get_google_id(url):
    matched = re.search("\/d\/(.*)\/", url)
    return matched.group(1)


class ScrapeWorker:
    def __init__(
        self,
        playwright,
        browser: Browser,
        scrape_task: SiteScrapeTask,
        site: Site,
    ) -> None:
        self.playwright = playwright
        self.browser = browser
        self.scrape_task = scrape_task
        self.site = site
        self.seen_urls = set()
        self.doc_client = DocumentStorageClient()
        self.downloader = AioDownloader()
        self.logger = Logger()

    @alru_cache
    async def get_user(self) -> User:
        user = await User.by_email("admin@mmitnetwork.com")
        if not user:
            raise Exception("No user found")
        return user

    @alru_cache
    async def get_proxy_settings(
        self,
    ) -> list[tuple[Proxy | None, ProxySettings | None]]:
        proxies = await Proxy.find_all().to_list()
        proxy_exclusions = self.site.scrape_method_configuration.proxy_exclusions
        valid_proxies = [proxy for proxy in proxies if proxy.id not in proxy_exclusions]
        return convert_proxies_to_proxy_settings(valid_proxies)

    def skip_url(self, url):
        parsed = urlparse(url)
        if parsed.scheme not in ["https", "http"]:  # mailto, tel, etc
            return True
        return False

    def url_not_seen(self, url, filename: str = ""):
        # skip if we've already seen this url
        if url in self.seen_urls:
            return False
        self.seen_urls.add(f"{url}{filename}")
        return True

    async def attempt_download(self, download: Download):
        url = download.request.url
        proxies = await self.get_proxy_settings()
        async for (temp_path, checksum) in self.downloader.download_to_tempfile(
            download, proxies
        ):
            await self.scrape_task.update(Inc({SiteScrapeTask.documents_found: 1}))

            parsed_content = await parse_by_type(temp_path, download)
            if parsed_content is None:
                continue

            now = datetime.now()
            dest_path = f"{checksum}.{download.file_extension}"
            document = None

            if not self.doc_client.document_exists(dest_path):
                self.doc_client.write_document(dest_path, temp_path)
                await self.scrape_task.update(
                    Inc({SiteScrapeTask.new_documents_found: 1})
                )
            else:
                document = await RetrievedDocument.find_one(
                    RetrievedDocument.checksum == checksum
                )

            if document:
                updates = UpdateRetrievedDocument(
                    context_metadata=download.metadata.dict(),
                    doc_type_confidence=parsed_content["confidence"],
                    document_type=parsed_content["document_type"],
                    effective_date=parsed_content["effective_date"],
                    identified_dates=parsed_content["identified_dates"],
                    lang_code=parsed_content["lang_code"],
                    last_collected_date=now,
                    metadata=parsed_content["metadata"],
                    name=parsed_content["title"],
                    scrape_task_id=self.scrape_task.id,
                )
                await update_and_log_diff(
                    self.logger, await self.get_user(), document, updates
                )
            else:
                document = RetrievedDocument(
                    base_url=download.metadata.base_url,
                    checksum=checksum,
                    context_metadata=download.metadata.dict(),
                    doc_type_confidence=parsed_content["confidence"],
                    document_type=parsed_content["document_type"],
                    effective_date=parsed_content["effective_date"],
                    file_extension=download.file_extension,
                    first_collected_date=now,
                    identified_dates=parsed_content["identified_dates"],
                    lang_code=parsed_content["lang_code"],
                    last_collected_date=now,
                    metadata=parsed_content["metadata"],
                    name=parsed_content["title"],
                    scrape_task_id=self.scrape_task.id,
                    site_id=self.site.id,
                    url=url,
                )
                await create_and_log(self.logger, await self.get_user(), document)
            await self.scrape_task.update(
                Push({SiteScrapeTask.retrieved_document_ids: document.id})
            )

    async def watch_for_cancel(self, tasks: list[asyncio.Task[None]]):
        while True:
            if all(t.done() for t in tasks):
                break
            canceling = await SiteScrapeTask.find_one(
                SiteScrapeTask.id == self.scrape_task.id,
                SiteScrapeTask.status == Status.CANCELING,
            )
            if canceling:
                for t in tasks:
                    t.cancel()
                raise CanceledTaskException("Task was canceled.")
            await asyncio.sleep(1)

    async def wait_for_completion_or_cancel(
        self, downloads: list[Coroutine[None, None, None]]
    ):

        if len(downloads) == 0:
            raise NoDocsCollectedException("No documents collected.")

        tasks = [asyncio.create_task(download) for download in downloads]

        try:
            await asyncio.gather(self.watch_for_cancel(tasks), *tasks)
        except asyncio.exceptions.CancelledError:
            pass

    async def try_each_proxy(self):
        """
        Try each proxy in turn, if it fails, try the next one. Repeat a few times for good measure.
        """
        proxy_settings = await self.get_proxy_settings()
        shuffle(proxy_settings)
        n_proxies = len(proxy_settings)
        async for attempt in AsyncRetrying(stop=stop_after_attempt(3 * n_proxies)):
            i = attempt.retry_state.attempt_number - 1
            proxy, proxy_setting = proxy_settings[i % n_proxies]
            logging.info(
                f"{i} Trying proxy {proxy and proxy.name} - {proxy_setting and proxy_setting.get('server')}"
            )
            yield attempt, proxy_setting

    @asynccontextmanager
    async def playwright_context(self, url: str) -> AsyncGenerator[Page, None]:
        logging.info(f"Creating context for {url}")
        context: BrowserContext | None = None
        page: Page | None = None
        async for attempt, proxy in self.try_each_proxy():
            with attempt:
                context = await self.browser.new_context(
                    proxy=proxy,
                    ignore_https_errors=True,
                )  # type: ignore

                page = await context.new_page()
                await stealth_async(page)
                await page.goto(
                    url,
                    wait_until="domcontentloaded",
                    timeout=60000,
                )

        if not page:
            raise Exception(f"Could not load {url}")

        try:
            yield page, context
        finally:
            if context:
                await context.close()

    def active_base_urls(self):
        return [url for url in self.site.base_urls if url.status == "ACTIVE"]

    async def queue_downloads(self, url, base_url: str | None = None):
        all_downloads: list[Download] = []
        page: Page
        context: BrowserContext
        async with self.playwright_context(url) as (page, context):
            for Scraper in scrapers:
                scraper: Type[PlaywrightBaseScraper] = Scraper(
                    page=page,
                    context=context,
                    config=self.site.scrape_method_configuration,
                    url=url,
                )

                if not await scraper.is_applicable():
                    continue

                downloads = await scraper.execute()

                download: Download
                for download in downloads:
                    download.metadata.base_url = base_url or url
                    # TODO where this lives ... also office live?
                    if is_google(download.request.url):
                        google_id = get_google_id(download.request.url)
                        download.request.url = f"https://drive.google.com/u/0/uc?id={google_id}&export=download"

                all_downloads += downloads

            return all_downloads

    async def crawl_page(self, url):
        urls: list[str] = []
        page: Page
        context: BrowserContext
        async with self.playwright_context(url) as (page, context):

            crawler: FollowLinkScraper = FollowLinkScraper(
                page=page,
                context=context,
                config=self.site.scrape_method_configuration,
                url=url,
            )

            if await crawler.is_applicable():
                urls = await crawler.execute()

            return {"base_url": url, "crawled_urls": urls}

    async def run_scrape(self):
        all_downloads: list[Download] = []
        base_urls: list[str] = [base_url.url for base_url in self.active_base_urls()]

        for url in base_urls:
            result = await self.crawl_page(url)
            for nested_url in result["crawled_urls"]:
                all_downloads += await self.queue_downloads(
                    nested_url, base_url=result["base_url"]
                )
            if result["base_url"] != url:
                all_downloads += await self.queue_downloads(url)

        tasks = []
        for download in all_downloads:
            url = download.request.url
            # check that the link is unique and that we should not skip it
            if not self.skip_url(url) and self.url_not_seen(
                url, download.response.content_disposition_filename
            ):
                await self.scrape_task.update(Inc({SiteScrapeTask.links_found: 1}))
                tasks.append(
                    self.attempt_download(
                        download,
                    )
                )

        await self.wait_for_completion_or_cancel(tasks)

        await self.downloader.close()
