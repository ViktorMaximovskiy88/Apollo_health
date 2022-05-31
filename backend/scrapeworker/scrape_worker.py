import asyncio
from contextlib import asynccontextmanager
from datetime import datetime
import os
import pathlib
from beanie.odm.operators.update.general import Inc
from urllib.parse import urlparse, urljoin
from backend.common.models.site import Site
from backend.common.models.document import RetrievedDocument, UpdateRetrievedDocument
from backend.common.models.site_scrape_task import SiteScrapeTask
from playwright.async_api import ElementHandle
from playwright_stealth import stealth_async
from backend.common.models.user import User
from backend.scrapeworker.doc_type_classifier import classify_doc_type
from backend.scrapeworker.downloader import DocDownloader
from backend.scrapeworker.effective_date import extract_dates, select_effective_date
from backend.scrapeworker.proxy import proxy_settings
from backend.scrapeworker.rate_limiter import RateLimiter

from backend.app.utils.logger import Logger, create_and_log, update_and_log_diff
from backend.common.storage.client import DocumentStorageClient
from backend.scrapeworker.xpdf_wrapper import pdfinfo, pdftotext


class ScrapeWorker:
    def __init__(self, playwright, browser, scrape_task: SiteScrapeTask, site: Site) -> None:
        self.playwright = playwright
        self.browser = browser
        self.scrape_task = scrape_task
        self.site = site
        self.seen_urls = []
        self.rate_limiter = RateLimiter()
        self.doc_client = DocumentStorageClient()
        self.downloader = DocDownloader(playwright, self.seen_urls, self.rate_limiter)
        self.logger = Logger()
        self.user = None

    async def get_user(self):
        if not self.user:
            self.user = await User.by_email("admin@mmitnetwork.com")
        if not self.user:
            raise Exception("No user found")
        return self.user

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
        return url, {"link_text": link_text, "closest_heading": closest_heading}

    def skip_url(self, url):
        parsed = urlparse(url)
        if parsed.scheme not in ["https", "http"]:  # mailto, tel, etc
            return True
        if url in self.seen_urls:  # skip if we've already seen this url
            return True
        return False

    def select_title(self, metadata, url):
        filename_no_ext = pathlib.Path(os.path.basename(url)).with_suffix("")
        title = metadata.get("Title") or metadata.get("Subject") or str(filename_no_ext)
        return title

    async def attempt_download(self, url, context_metadata):
        
        async for (temp_path, checksum) in self.downloader.download_to_tempfile(url):
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
            document_type, _ = classify_doc_type(text)

            now = datetime.now()
            datelist = list(dates.keys())
            datelist.sort()

            if document:
                updates = UpdateRetrievedDocument(
                    context_metadata=context_metadata,
                    effective_date=effective_date,
                    document_type=document_type,
                    metadata=metadata,
                    identified_dates=datelist,
                    scrape_task_id=self.scrape_task.id,
                    last_seen=now,
                    name=title,
                )
                await update_and_log_diff(
                    self.logger, await self.get_user(), document, updates
                )
            else:
                document = RetrievedDocument(
                    name=title,
                    document_type=document_type,
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
        context = await self.browser.new_context(proxy=proxy_settings())
        page = await context.new_page()
        await stealth_async(page)
        await page.goto(base_url, wait_until="networkidle") #await page.goto(base_url, wait_until="domcontentloaded")#
        try:
            yield page
        finally:
            await page.close()

    async def run_scrape(self):
        async with self.playwright_context(self.site.base_url) as page:
            link_handles = await page.query_selector_all("a[href$=pdf]")
            print(f"Found {len(link_handles)} links")
            downloads = []
            urls=set()
            for link_handle in link_handles:
                url, context_metadata = await self.extract_url_and_context_metadata(link_handle)       
       
                #check that think link is unique
                if not url in urls:
                    urls.add(url)
                    if not self.skip_url(url):
                        await self.scrape_task.update(Inc({SiteScrapeTask.links_found: 1}))
                        downloads.append(self.attempt_download(url, context_metadata))
            await asyncio.gather(*downloads)
