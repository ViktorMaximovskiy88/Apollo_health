import asyncio
import logging
import re
from contextlib import asynccontextmanager
from datetime import datetime
from random import shuffle
from typing import AsyncGenerator, Coroutine
from async_lru import alru_cache
from tenacity.wait import wait_random_exponential
from tenacity._asyncio import AsyncRetrying
from tenacity.stop import stop_after_attempt
from beanie.odm.operators.update.array import Push
from beanie.odm.operators.update.general import Inc
from urllib.parse import urlparse 
from backend.common.models.doc_document import DocDocument
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
from backend.scrapeworker.common.aio_downloader import AioDownloader
from backend.scrapeworker.common.proxy import convert_proxies_to_proxy_settings
from backend.app.utils.logger import Logger, create_and_log, update_and_log_diff
from backend.common.storage.client import DocumentStorageClient
from backend.scrapeworker.common.exceptions import (
    CanceledTaskException,
)
from backend.scrapeworker.common.models import Download
from backend.scrapeworker.scrapers import scrapers
from backend.scrapeworker.scrapers.follow_link import FollowLinkScraper
from backend.scrapeworker.common.proxy import convert_proxies_to_proxy_settings
from backend.scrapeworker.common.aio_downloader import default_headers
from backend.app.utils.logger import Logger, create_and_log, update_and_log_diff
from backend.common.storage.client import DocumentStorageClient
from backend.scrapeworker.file_parsers import parse_by_type
from backend.common.core.enums import TaskStatus
from scrapeworker.document_tagging.indication_tagging import IndicationTagger
from scrapeworker.document_tagging.taggers import Taggers
from scrapeworker.document_tagging.therapy_tagging import TherapyTagger
from scrapeworker.playbook import ScrapePlaybook


def is_google(url):
    parsed = urlparse(url)
    return parsed.hostname in ["drive.google.com", "docs.google.com"]


def get_google_id(url: str) -> str:
    matched = re.search(r"/d/(.*)/", url)
    if not matched:
        raise Exception(f"{url} is not a valid google doc/drive url")
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
        self.playbook = ScrapePlaybook(self.site.playbook)
        self.logger = Logger()
        self.taggers = Taggers(
            indication=IndicationTagger(),
            therapy=TherapyTagger()
        )

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

    def url_not_seen(self, url, filename: str | None):
        # skip if we've already seen this url
        if url in self.seen_urls:
            return False
        key = f"{url}{filename}" if filename else url
        logging.info(f"unseen target -> {key}")
        self.seen_urls.add(key)
        return True

    async def update_doc_document(self, retrieved_document: RetrievedDocument):
        doc_document = await DocDocument.find_one(DocDocument.retrieved_document_id == retrieved_document.id)
        if doc_document:
            await doc_document.update({
                '$set': {
                    'last_collected_date': retrieved_document.last_collected_date
                }
            })
        else:
            await self.create_doc_document(retrieved_document)

    async def create_doc_document(self, retrieved_document: RetrievedDocument):
        doc_document = DocDocument(
            site_id=retrieved_document.site_id,
            retrieved_document_id=retrieved_document.id,  # type: ignore
            name=retrieved_document.name,
            checksum=retrieved_document.checksum,

            document_type=retrieved_document.document_type,
            doc_type_confidence=retrieved_document.doc_type_confidence,

            end_date=retrieved_document.end_date,
            effective_date=retrieved_document.effective_date,
            last_updated_date=retrieved_document.last_updated_date,
            next_review_date=retrieved_document.next_review_date,
            next_update_date=retrieved_document.next_update_date,
            published_date=retrieved_document.published_date,

            lang_code=retrieved_document.lang_code,

            first_collected_date=retrieved_document.first_collected_date,
            last_collected_date=retrieved_document.last_collected_date,

            link_text=retrieved_document.context_metadata['link_text'],
            url=retrieved_document.url,
            base_url=retrieved_document.base_url,

            therapy_tags=retrieved_document.therapy_tags,
            indication_tags=retrieved_document.indication_tags,
        )
        await create_and_log(self.logger, await self.get_user(), doc_document)

    async def attempt_download(self, download: Download):
        url = download.request.url
        proxies = await self.get_proxy_settings()
        async for (temp_path, checksum) in self.downloader.download_to_tempfile(
            download, proxies
        ):
            await self.scrape_task.update(Inc({SiteScrapeTask.documents_found: 1}))

            parsed_content = await parse_by_type(temp_path, download, self.taggers)
            if parsed_content is None:
                continue

            now = datetime.now()
            dest_path = f"{checksum}.{download.file_extension}"
            document = None

            logging.info(f"dest_path={dest_path} temp_path={temp_path}")

            if not self.doc_client.object_exists(dest_path):
                self.doc_client.write_object(dest_path, temp_path)
                await self.scrape_task.update(
                    Inc({SiteScrapeTask.new_documents_found: 1})
                )
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
                    therapy_tags=parsed_content["therapy_tags"],
                    indication_tags=parsed_content["indication_tags"],
                    metadata=parsed_content["metadata"],
                    name=parsed_content["title"],
                    scrape_task_id=self.scrape_task.id,
                )
                await update_and_log_diff(
                    self.logger, await self.get_user(), document, updates
                )
                await self.update_doc_document(document)
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
                    therapy_tags=parsed_content["therapy_tags"],
                    indication_tags=parsed_content["indication_tags"],
                )
                await create_and_log(self.logger, await self.get_user(), document)
                await self.create_doc_document(document)
            await self.scrape_task.update(
                Push({SiteScrapeTask.retrieved_document_ids: document.id})
            )

    async def watch_for_cancel(self, tasks: list[asyncio.Task[None]]):
        while True:
            if all(t.done() for t in tasks):
                break
            canceling = await SiteScrapeTask.find_one(
                SiteScrapeTask.id == self.scrape_task.id,
                SiteScrapeTask.status == TaskStatus.CANCELING,
            )
            if canceling:
                for t in tasks:
                    t.cancel()
                raise CanceledTaskException("Task was canceled.")
            await asyncio.sleep(1)

    async def wait_for_completion_or_cancel(
        self, downloads: list[Coroutine[None, None, None]]
    ):
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
        async for attempt in AsyncRetrying(reraise=True, stop=stop_after_attempt(3 * n_proxies), wait=wait_random_exponential(multiplier=1, max=60)):
            i = attempt.retry_state.attempt_number - 1
            proxy, proxy_setting = proxy_settings[i % n_proxies]
            logging.info(
                f"{i} Trying proxy {proxy and proxy.name} - {proxy_setting and proxy_setting.get('server')}"
            )
            yield attempt, proxy_setting

    async def wait_for_desired_content(self, page: Page):
        try:
            if len(self.site.scrape_method_configuration.wait_for) > 0:
                await page.locator(
                    ", ".join(
                        f":text('{wf}')"
                        for wf in self.site.scrape_method_configuration.wait_for
                    )
                ).first.wait_for()
        except:
            raise Exception(
                f"Wait for dom elements {self.site.scrape_method_configuration.wait_for} have timed out"
            )

    @asynccontextmanager
    async def playwright_context(self, url: str) -> AsyncGenerator[tuple[Page, BrowserContext], None]:
        logging.info(f"Creating context for {url}")
        context: BrowserContext | None = None
        page: Page | None = None
        async for attempt, proxy in self.try_each_proxy():
            with attempt:
                context = await self.browser.new_context(
                    extra_http_headers=default_headers,
                    proxy=proxy,  # type: ignore
                    ignore_https_errors=True,
                )

                page = await context.new_page()
                await stealth_async(page)
                await page.goto(url, timeout=60000)

        if not page or not context:
            raise Exception(f"Could not load {url}")

        await self.wait_for_desired_content(page)

        try:
            yield page, context
        finally:
            if context:
                await context.close()

    def active_base_urls(self):
        return [url for url in self.site.base_urls if url.status == "ACTIVE"]

    def preprocess_download(self, download: Download, base_url: str):
        download.metadata.base_url = base_url
        # TODO where this lives ... also office live?
        if is_google(download.request.url):
            google_id = get_google_id(download.request.url)
            download.request.url = f"https://drive.google.com/u/0/uc?id={google_id}&export=download"

    async def queue_downloads(self, url: str, base_url: str):
        all_downloads: list[Download] = []
        async with self.playwright_context(url) as (base_page, context):
            async for (page, playbook_context) in self.playbook.run_playbook(base_page):
                for Scraper in scrapers:
                    scraper = Scraper(
                        page=page,
                        context=context,
                        config=self.site.scrape_method_configuration,
                        playbook_context=playbook_context,
                        url=url,
                    )

                    if not await scraper.is_applicable():
                        continue

                    for download in await scraper.execute():
                        self.preprocess_download(download, base_url)
                        all_downloads.append(download)

            return all_downloads

    async def follow_links(self, url) -> list[str]:
        urls: list[str] = []
        page: Page
        context: BrowserContext
        async with self.playwright_context(url) as (page, context):
            crawler = FollowLinkScraper(
                page=page,
                context=context,
                config=self.site.scrape_method_configuration,
                url=url,
            )

            if await crawler.is_applicable():
                for dl in await crawler.execute():
                    urls.append(dl.request.url)

            return urls

    def should_process_download(self, download: Download):
        url = download.request.url
        cd_filename = download.response.content_disposition_filename
        
        return not self.skip_url(url) and \
            self.url_not_seen(url, cd_filename)

    async def run_scrape(self):
        all_downloads: list[Download] = []
        base_urls: list[str] = [base_url.url for base_url in self.active_base_urls()]
        logging.info(f"base_urls={base_urls}")
        for url in base_urls:
            all_downloads += await self.queue_downloads(url, url)
            for nested_url in await self.follow_links(url):
                all_downloads += await self.queue_downloads(
                    nested_url, base_url=url
                )

        tasks = []
        for download in all_downloads:
            if self.should_process_download(download):
                await self.scrape_task.update(Inc({SiteScrapeTask.links_found: 1}))
                tasks.append(self.attempt_download(download))

        await self.wait_for_completion_or_cancel(tasks)
        await self.downloader.close()
