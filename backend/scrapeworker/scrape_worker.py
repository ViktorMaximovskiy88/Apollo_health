import asyncio
from contextlib import asynccontextmanager
from datetime import datetime
from random import shuffle
from typing import AsyncGenerator, Coroutine
from async_lru import alru_cache
import os
import pathlib
from tenacity._asyncio import AsyncRetrying
from tenacity.stop import stop_after_attempt
from beanie.odm.operators.update.general import Inc
from urllib.parse import urlparse, urljoin
from backend.common.models.proxy import Proxy
from backend.common.models.site import Site
from backend.common.models.document import RetrievedDocument, UpdateRetrievedDocument
from backend.common.models.site_scrape_task import SiteScrapeTask
from playwright.async_api import (
    ElementHandle,
    Browser,
    BrowserContext,
    ProxySettings,
    Page,
)
from playwright_stealth import stealth_async
from backend.common.models.user import User
from backend.scrapeworker.doc_type_classifier import classify_doc_type
from backend.scrapeworker.detect_lang import detect_lang
from backend.scrapeworker.downloader import DocDownloader
from backend.scrapeworker.effective_date import extract_dates, select_effective_date
from backend.scrapeworker.proxy import convert_proxies_to_proxy_settings
from backend.app.utils.logger import Logger, create_and_log, update_and_log_diff
from backend.common.storage.client import DocumentStorageClient
from backend.scrapeworker.xpdf_wrapper import pdfinfo, pdftotext


class CanceledTaskException(Exception):
    pass


class ScrapeWorker:
    def __init__(
        self, playwright, browser: Browser, scrape_task: SiteScrapeTask, site: Site
    ) -> None:
        self.playwright = playwright
        self.browser = browser
        self.scrape_task = scrape_task
        self.site = site
        self.seen_urls = set()
        self.doc_client = DocumentStorageClient()
        self.downloader = DocDownloader(playwright)
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

    async def extract_url_and_context_metadata(
        self, base_url: str, link_handle: ElementHandle
    ):
        href = await link_handle.get_attribute("href")
        link_text = await link_handle.text_content()
        closest_heading_expression = """
        (node) => {
            let n = node;
            while (n) {
                const h = n.querySelector('h1, h2, h3, h4, h5, h6')
                if (h) return h.textContent;
                n = n.parentNode;
            }
        }
        """
        closest_heading = await link_handle.evaluate(closest_heading_expression)
        url = urljoin(base_url, href)
        return url, {"link_text": link_text, "closest_heading": closest_heading}

    def skip_url(self, url):
        parsed = urlparse(url)
        if parsed.scheme not in ["https", "http"]:  # mailto, tel, etc
            return True
        return False

    def url_not_seen(self, url):
        # skip if we've already seen this url
        if url in self.seen_urls:
            return False
        self.seen_urls.add(url)
        return True

    def select_title(self, metadata, url):
        filename_no_ext = pathlib.Path(os.path.basename(url)).with_suffix("")
        title = metadata.get("Title") or metadata.get("Subject") or str(filename_no_ext)
        return title

    async def attempt_download(self, base_url, url, context_metadata):
        proxies = await self.get_proxy_settings()
        async for (temp_path, checksum) in self.downloader.download_to_tempfile(
            url, proxies
        ):
            await self.scrape_task.update(Inc({SiteScrapeTask.documents_found: 1}))
            dest_path = f"{checksum}.pdf"
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

            metadata = await pdfinfo(temp_path)
            text = await pdftotext(temp_path)
            dates = extract_dates(text)
            effective_date = select_effective_date(dates)
            title = self.select_title(metadata, url)
            document_type, confidence = classify_doc_type(text)
            lang_code = detect_lang(text)
            print(f"{url} as {lang_code}")

            now = datetime.now()
            datelist = list(dates.keys())
            datelist.sort()

            if document:
                updates = UpdateRetrievedDocument(
                    context_metadata=context_metadata,
                    effective_date=effective_date,
                    document_type=document_type,
                    doc_type_confidence=confidence,
                    metadata=metadata,
                    identified_dates=datelist,
                    scrape_task_id=self.scrape_task.id,
                    last_seen=now,
                    name=title,
                    lang_code=lang_code,
                )
                await update_and_log_diff(
                    self.logger, await self.get_user(), document, updates
                )
            else:
                document = RetrievedDocument(
                    name=title,
                    document_type=document_type,
                    doc_type_confidence=confidence,
                    effective_date=effective_date,
                    identified_dates=list(dates.keys()),
                    scrape_task_id=self.scrape_task.id,
                    site_id=self.site.id,
                    collection_time=now,
                    last_seen=now,
                    checksum=checksum,
                    url=url,
                    context_metadata=context_metadata,
                    metadata=metadata,
                    base_url=base_url,
                    lang_code=lang_code,
                )
                await create_and_log(self.logger, await self.get_user(), document)

    async def watch_for_cancel(self, tasks: list[asyncio.Task[None]]):
        while True:
            if all(t.done() for t in tasks):
                break
            canceling = await SiteScrapeTask.find_one(
                SiteScrapeTask.id == self.scrape_task.id,
                SiteScrapeTask.status == "CANCELING",
            )
            if canceling:
                for t in tasks:
                    t.cancel()
                raise CanceledTaskException("Task was canceled.")
            await asyncio.sleep(1)

    async def wait_for_completion_or_cancel(self, downloads: list[Coroutine[None, None, None]]):
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
        async for attempt in AsyncRetrying(stop=stop_after_attempt(3*n_proxies)):
            i = attempt.retry_state.attempt_number - 1
            proxy, proxy_setting = proxy_settings[i % n_proxies]
            print(f"{i} Trying proxy {proxy and proxy.name} - {proxy_setting and proxy_setting.get('server')}")
            yield attempt, proxy_setting

    @asynccontextmanager
    async def playwright_context(self, base_url: str) -> AsyncGenerator[Page, None]:
        print(f"Creating context for {base_url}")
        context: BrowserContext | None = None
        page: Page | None = None
        async for attempt, proxy in self.try_each_proxy():
            with attempt:
                context = await self.browser.new_context(proxy=proxy) # type: ignore
                page = await context.new_page()
                await stealth_async(page)
                await page.goto(base_url, wait_until="domcontentloaded") # await page.goto(base_url, wait_until="networkidle")

        if not page:
            raise Exception(f"Could not load {base_url}")

        try:
            yield page
        finally:
            if context:
                await context.close()

    def construct_selector(self):
        extensions = self.site.scrape_method_configuration.document_extensions
        keywords = self.site.scrape_method_configuration.url_keywords
        ext_selectors = [f'a[href$="{ext}"]' for ext in extensions]
        wrd_selectors = [f'a[href*="{word}"]' for word in keywords]
        selector = ",".join(ext_selectors + wrd_selectors)
        return selector

    def active_base_urls(self):
        return [url for url in self.site.base_urls if url.status == "ACTIVE"]

    async def run_scrape(self):
        for base_url in self.active_base_urls():
            async with self.playwright_context(base_url.url) as page:
                link_handles = await page.query_selector_all(self.construct_selector())
                print(f"Found {len(link_handles)} links")
                downloads = []
                for link_handle in link_handles:
                    url, context_metadata = await self.extract_url_and_context_metadata(
                        base_url.url, link_handle
                    )

                    # check that think link is unique and that we should not skip it
                    if not self.skip_url(url) and self.url_not_seen(url):
                        await self.scrape_task.update(
                            Inc({SiteScrapeTask.links_found: 1})
                        )
                        downloads.append(
                            self.attempt_download(base_url.url, url, context_metadata)
                        )
                await self.wait_for_completion_or_cancel(downloads)
