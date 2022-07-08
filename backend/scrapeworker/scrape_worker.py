import asyncio
import re
from contextlib import asynccontextmanager
from datetime import datetime
from random import shuffle
from typing import AsyncGenerator, Callable, Coroutine
from async_lru import alru_cache
import os
import pathlib
from tenacity._asyncio import AsyncRetrying
from tenacity.stop import stop_after_attempt
from beanie.odm.operators.update.array import Push
from beanie.odm.operators.update.general import Inc
from urllib.parse import urlparse, urljoin
from backend.common.models.proxy import Proxy
from backend.common.models.site import BaseUrl, Site
from backend.common.models.document import RetrievedDocument, UpdateRetrievedDocument
from backend.common.models.site_scrape_task import SiteScrapeTask
from playwright.async_api import (
    ElementHandle,
    Browser,
    BrowserContext,
    ProxySettings,
    Page,
    Request,
)
from playwright_stealth import stealth_async
from backend.common.models.user import User
from backend.scrapeworker.downloader import DocDownloader
from backend.scrapeworker.proxy import convert_proxies_to_proxy_settings
from backend.app.utils.logger import Logger, create_and_log, update_and_log_diff
from backend.common.storage.client import DocumentStorageClient
from backend.scrapeworker.file_parsers import parse_by_type
from backend.common.core.enums import TaskStatus

# Scrapeworker workflow 'exceptions'
class NoDocsCollectedException(Exception):
    pass


class CanceledTaskException(Exception):
    pass


def get_extension(url_or_path: str):
    return pathlib.Path(os.path.basename(url_or_path)).suffix[1:]


def is_google(url):
    parsed = urlparse(url)
    return parsed.hostname in ["drive.google.com", "docs.google.com"]


def get_google_id(url):
    matched = re.search("\/d\/(.*)\/", url)
    return matched.group(1)


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

    async def attempt_download(self, base_url, url, context_metadata):
        proxies = await self.get_proxy_settings()
        async for (
            temp_path,
            checksum,
        ) in self.downloader.download_to_tempfile(url, proxies):
            await self.scrape_task.update(Inc({SiteScrapeTask.documents_found: 1}))

            file_extension = get_extension(temp_path)
            dest_path = f"{checksum}.{file_extension}"
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

            parsed_content = await parse_by_type(temp_path, url)
            now = datetime.now()

            if document:
                updates = UpdateRetrievedDocument(
                    context_metadata=context_metadata,
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
                    base_url=base_url,
                    checksum=checksum,
                    context_metadata=context_metadata,
                    doc_type_confidence=parsed_content["confidence"],
                    document_type=parsed_content["document_type"],
                    effective_date=parsed_content["effective_date"],
                    first_collected_date=now,
                    identified_dates=parsed_content["identified_dates"],
                    lang_code=parsed_content["lang_code"],
                    last_collected_date=now,
                    metadata=parsed_content["metadata"],
                    name=parsed_content["title"],
                    scrape_task_id=self.scrape_task.id,
                    site_id=self.site.id,
                    url=url,
                    file_extension=file_extension,
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
            print(
                f"{i} Trying proxy {proxy and proxy.name} - {proxy_setting and proxy_setting.get('server')}"
            )
            yield attempt, proxy_setting

    @asynccontextmanager
    async def playwright_context(self, url: str) -> AsyncGenerator[Page, None]:
        print(f"Creating context for {url}")
        context: BrowserContext | None = None
        page: Page | None = None
        async for attempt, proxy in self.try_each_proxy():
            with attempt:
                context = await self.browser.new_context(proxy=proxy, ignore_https_errors=True)  # type: ignore
                page = await context.new_page()
                await stealth_async(page)
                await page.goto(base_url, wait_until="domcontentloaded") # await page.goto(base_url, wait_until="networkidle")
                
                try:
                    if len(self.site.scrape_method_configuration.wait_for) > 0:
                        await page.locator("body", has=page.locator(', '.join(f":text('{wf}')" for wf in self.site.scrape_method_configuration.wait_for))).wait_for(state="attached")
                except:
                    raise Exception(f"Wait for dom elements {self.site.scrape_method_configuration.wait_for} have timed out")
                    
        if not page:
            raise Exception(f"Could not load {url}")

        try:
            yield page
        finally:
            if context:
                await context.close()

    def construct_follow_links_selector(self) -> str:
        keywords = self.site.scrape_method_configuration.follow_link_keywords
        url_keywords = self.site.scrape_method_configuration.follow_link_url_keywords
        wrd_selectors = [f'a:has-text("{word}")' for word in keywords]
        url_selectors = [f'a[href*="{word}"]' for word in url_keywords]
        selector = ",".join(wrd_selectors + url_selectors)
        return selector

    def construct_selector(self) -> str:
        extensions = self.site.scrape_method_configuration.document_extensions
        keywords = self.site.scrape_method_configuration.url_keywords
        ext_selectors = [f'a[href$="{ext}"]' for ext in extensions]
        wrd_selectors = [f'a[href*="{word}"]' for word in keywords]
        selector = ",".join(ext_selectors + wrd_selectors)
        return selector

    def active_base_urls(self):
        return [url for url in self.site.base_urls if url.status == "ACTIVE"]

    async def queue_downloads(
        self,
        base_url: BaseUrl,
        page: Page = None,
        url: str = None,
        context_metadata: dict[str] = None,
    ):
        """
        Scrape provided page for urls to download. Create new page if no page provided.
        Queue downloads of scraped urls or pdfs from network requests.
        """
        downloads = []
        link_handles = await page.query_selector_all(self.construct_selector())
        print(f"Found {len(link_handles)} links")
        for link_handle in link_handles:
            url, context_metadata = await self.extract_url_and_context_metadata(
                base_url.url, link_handle
            )

            if is_google(url):
                google_id = get_google_id(url)
                url = f"https://drive.google.com/u/0/uc?id={google_id}&export=download"

            # check that link is unique and that we should not skip it
            if not self.skip_url(url) and self.url_not_seen(url):
                await self.scrape_task.update(Inc({SiteScrapeTask.links_found: 1}))
                downloads.append(
                    self.attempt_download(base_url.url, url, context_metadata)
                )
        return downloads

    async def run_scrape(self):
        for base_url in self.active_base_urls():
            async with self.playwright_context(base_url.url) as page:
                downloads = []
                if self.site.scrape_method_configuration.follow_links:
                    selector = self.construct_follow_links_selector()
                    follow_handles = await page.query_selector_all(selector)
                    for handle in follow_handles:
                        href = await handle.get_attribute("href")
                        url = urljoin(base_url.url, href)
                        try:
                            async with self.playwright_context(url) as sub_page:
                                downloads += await self.queue_downloads(
                                    base_url, page=sub_page
                                )
                        except:
                            continue
                downloads += await self.queue_downloads(base_url, page=page)
                await self.wait_for_completion_or_cancel(downloads)
