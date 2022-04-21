import asyncio
import redis
from contextlib import asynccontextmanager
from datetime import datetime
import xxhash
import tempfile
import os
import pathlib
import random
import re
import aiofiles
from tenacity._asyncio import AsyncRetrying
from dateutil import parser
from beanie.odm.operators.update.general import Inc
from urllib.parse import urlparse, urljoin
from backend.common.models.site import Site
from backend.common.models.document import RetrievedDocument, UpdateRetrievedDocument
from backend.common.models.site_scrape_task import SiteScrapeTask
from playwright.async_api import async_playwright, ElementHandle, Playwright, APIResponse
from playwright_stealth import stealth_async
from backend.common.models.user import User
from backend.common.core.config import config

from backend.app.utils.logger import Logger, create_and_log, update_and_log_diff
from backend.common.storage.client import DocumentStorageClient


class ScrapeWorker:
    def __init__(self, scrape_task: SiteScrapeTask, site: Site) -> None:
        self.scrape_task = scrape_task
        self.site = site
        self.last_request_time = datetime.now()
        self.wait_between_requests = 1
        self.seen_urls = []
        self.doc_client = DocumentStorageClient()
        self.logger = Logger()
        self.redis = redis.from_url(config['REDIS_URL'], password=config['REDIS_PASSWORD'])
        self.user = None

    async def get_user(self):
        if not self.user:
            self.user = await User.by_email("admin@mmitnetwork.com")
        if not self.user:
            raise Exception("No user found")
        return self.user

    content_types = ["application/pdf"]

    def wait_exponential_backoff(self, retry_state):
        time_since_last_request = datetime.now() - self.last_request_time
        remaining_wait = (
            self.wait_between_requests - time_since_last_request.total_seconds()
        )
        if remaining_wait > 0:
            return remaining_wait + random.random()
        else:
            return 0

    def increase_exponential_backoff(self, retry_state):
        self.wait_between_requests *= 2
        print(f"Wait set to {self.wait_between_requests}")

    async def extract_url_and_context_metadata(self, link_handle: ElementHandle):
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
        url = urljoin(self.site.base_url, href)
        return url, { "link_text": link_text, "closest_heading": closest_heading }

    def skip_url(self, url):
        parsed = urlparse(url)
        base = urlparse(self.site.base_url)
        if base.netloc != parsed.netloc: # skip if url is not a different page
            return True
        if parsed.scheme not in ["https", "http"]: # mailto, tel, etc
            return True
        if url in self.seen_urls: # skip if we've already seen this url
            return True
        return False

    async def extract_pdf_metadata(self, dest_path):
        process = await asyncio.create_subprocess_exec(
            "pdfinfo",
            dest_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        pdfinfo_out, _ = await process.communicate()
        info = pdfinfo_out.decode("utf-8", "ignore").strip()
        metadata = {}
        for line in info.split("\n"):
            if not line.strip():
                continue
            key, value = line.split(":", 1)
            value = value.strip()
            metadata[key] = value
        return metadata

    async def extract_pdf_text(self, dest_path):
        process = await asyncio.create_subprocess_exec(
            "pdftotext",
            dest_path,
            "-",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        pdftext_out, _ = await process.communicate()
        return pdftext_out.decode("utf-8", "ignore").strip()

    def extract_dates(self, text):
        dates: dict[datetime, int] = {}

        date_formats = [
            "[0-9]{4}-[0-9][0-9]?-[0-9][0-9]?",  # yyyy-MM-dd
            "[0-9]{4}/[0-9][0-9]?/[0-9][0-9]?",  # yyyy/MM/dd
            "[0-9][0-9]?-[0-9][0-9]?-[0-9]{4}",  # dd-MM-yyyy
            "[0-9][0-9]?/[0-9][0-9]?/[0-9]{4}",  # dd/MM/yyyy
            "(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) [0-9][0-9]?, [0-9][0-9][0-9][0-9]",  # M d, yyyy
            "(January|February|March|April|May|June|July|August|September|October|November|December) [0-9][0-9]?, [0-9][0-9][0-9][0-9]",  # M d, yyyy
            "(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec),? [0-9][0-9][0-9][0-9]",  # M d, yyyy
            "(January|February|March|April|May|June|July|August|September|October|November|December),? [0-9][0-9][0-9][0-9]",  # M d, yyyy
        ]
        date_rgxs = [re.compile(fmt) for fmt in date_formats]
        for line in text.split("\n"):
            for rgx in date_rgxs:
                match = rgx.finditer(line)
                if match:
                    for m in match:
                        try:
                            date = parser.parse(m.group())
                        except:
                            continue
                        dates.setdefault(date, 0)
                        dates[date] += 1
        return dates

    def select_effective_date(self, dates):
        most_common_count = 0
        most_common_date = None
        for date, count in dates.items():
            if count > most_common_count:
                most_common_date = date
                most_common_count = count
        return most_common_date

    def select_title(self, metadata, url):
        filename_no_ext = pathlib.Path(os.path.basename(url)).with_suffix("")
        title = metadata.get("Title") or metadata.get("Subject") or str(filename_no_ext)
        return title

    def skip_based_on_response(self, response: APIResponse):
        if response.headers["content-type"] not in self.content_types:
            return True
        return False

    @asynccontextmanager
    async def playwright_request_context(self, playwright: Playwright):
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Pragma": "no-cache",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36",
        }
        context = await playwright.request.new_context(extra_http_headers=headers)
        try:
            yield context
        finally:
            await context.dispose()

    @asynccontextmanager
    async def download_url(self, url, playwright: Playwright):
        async with self.playwright_request_context(playwright) as context:
            self.seen_urls.append(url)
            response: APIResponse | None = None
            async for attempt in AsyncRetrying(wait=self.wait_exponential_backoff, before_sleep=self.increase_exponential_backoff):
                with attempt:
                    response = await context.get(url)
            if not response:
                raise Exception(f"Failed to download url {url}")

            print(f"Downloaded {url}, got {response.status}")
            try:
                assert response.ok
                yield response
            finally:
                await response.dispose()

    @asynccontextmanager
    async def tempfile_path(self, url: str, body: bytes):
        hash = xxhash.xxh128()
        with tempfile.NamedTemporaryFile() as temp:
            print(f"writing {url} file to tempfile {temp.name}")
            async with aiofiles.open(temp.name, "wb") as fd:
                hash.update(body)
                await fd.write(body)
            yield temp.name, hash.hexdigest()

    @asynccontextmanager
    async def download_to_tempfile(self, url: str, p: Playwright):
        body = self.redis.get(url)
        if body == 'DISCARD': return

        if body:
            print(f"Using cached {url}")
        else:
            print(f"Attempting download {url}")
            async with self.download_url(url, p) as response:
                if self.skip_based_on_response(response):
                    self.redis.set(url, 'DISCARD', ex=60*60*1) # 1 hour
                    return
                body = await response.body()
                self.redis.set(url, body, ex=60*60*1) # 1 hour

        async with self.tempfile_path(url, body) as (temp_path, hash):
            yield temp_path, hash

    async def attempt_download(self, link_handle: ElementHandle, p: Playwright):
        url, context_metadata = await self.extract_url_and_context_metadata(link_handle)
        if self.skip_url(url):
            return

        async with self.download_to_tempfile(url, p) as (temp_path, checksum):
            await self.scrape_task.update(Inc({SiteScrapeTask.documents_found: 1}))

            dest_path = f"{checksum}.pdf"
            document = None
            if not self.doc_client.document_exists(dest_path):
                self.doc_client.write_document(dest_path, temp_path)
                await self.scrape_task.update(Inc({SiteScrapeTask.new_documents_found: 1}))
            else:
                document = await RetrievedDocument.find_one(RetrievedDocument.checksum == checksum)

            metadata = await self.extract_pdf_metadata(temp_path)
            text = await self.extract_pdf_text(temp_path)
            dates = self.extract_dates(text)
            effective_date = self.select_effective_date(dates)
            title = self.select_title(metadata, url)

            now = datetime.now()
            if document:
                updates = UpdateRetrievedDocument(
                    context_metadata=context_metadata,
                    effective_date=effective_date,
                    metadata=metadata,
                    identified_dates=list(dates.keys()),
                    scrape_task_id=self.scrape_task.id,
                    last_seen=now,
                    name=title,
                )
                await update_and_log_diff(self.logger, await self.get_user(), document, updates)
            else:
                document = RetrievedDocument(
                    name=title,
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
                )
                await create_and_log(self.logger, await self.get_user(), document)

    @asynccontextmanager
    async def playwright_context(self, base_url):
        print(f"Creating context for {base_url}")
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await stealth_async(page)
            await page.goto(base_url)
            try:
                yield p, page
            finally:
                await browser.close()
        
    async def run_scrape(self):
        async with self.playwright_context(self.site.base_url) as (p, page):
            link_handles = await page.query_selector_all("a[href$=pdf]")
            print(f"Found {len(link_handles)} links")
            downloads = []
            for link_handle in link_handles:
                downloads.append(self.attempt_download(link_handle, p))
            await asyncio.gather(*downloads)
