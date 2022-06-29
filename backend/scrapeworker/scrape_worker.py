import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from random import shuffle
from turtle import down
from typing import AsyncGenerator, Coroutine
from async_lru import alru_cache
import os
import pathlib
from tenacity._asyncio import AsyncRetrying
from tenacity.stop import stop_after_attempt
from beanie.odm.operators.update.array import Push
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
from backend.scrapeworker.common.detect_lang import detect_lang
from backend.scrapeworker.downloader import DocDownloader
from backend.scrapeworker.common.effective_date import extract_dates, select_effective_date
from backend.scrapeworker.common.proxy import convert_proxies_to_proxy_settings
from backend.app.utils.logger import Logger, create_and_log, update_and_log_diff
from backend.common.storage.client import DocumentStorageClient
from backend.scrapeworker.common.xpdf_wrapper import pdfinfo, pdftotext
from backend.scrapeworker.common.exceptions import NoDocsCollectedException, CanceledTaskException
from backend.scrapeworker.drivers.playwright.direct_download import PlaywrightDirectDownload
from backend.scrapeworker.common.models import Download
from backend.scrapeworker.strategies.direct_download import DirectDownloadStategy
from backend.common.models.site import ScrapeMethodConfiguration
from backend.scrapeworker.common.downloader.aiohttp_client import AioDownloader


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
        valid_proxies = [
            proxy for proxy in proxies if proxy.id not in proxy_exclusions]
        return convert_proxies_to_proxy_settings(valid_proxies)

    def valid_scheme(self, url):
        parsed = urlparse(url)
        return parsed.scheme in ["https", "http"] # mailto, tel, etc

    def unqiue_url(self, url):
        # skip if we've already seen this url
        if url in self.seen_urls:
            return False
        self.seen_urls.add(url)
        return True

    def select_title(self, metadata, url):
        filename_no_ext = pathlib.Path(os.path.basename(url)).with_suffix("")
        title = metadata.get("Title") or metadata.get(
            "Subject") or str(filename_no_ext)
        return title

    async def try_download(self, download: Download, base_url):
        proxies = await self.get_proxy_settings()
        
        (temp_path, checksum, file_ext) = await self.downloader.download(download=download)
        await self.scrape_task.update(Inc({SiteScrapeTask.documents_found: 1}))

        dest_path = f"{checksum}.{file_ext}"
        document = None

        if not self.doc_client.document_exists(dest_path):
            logging.info(f'new doc {dest_path}')
            self.doc_client.write_document(dest_path, temp_path)
            await self.scrape_task.update(
                Inc({SiteScrapeTask.new_documents_found: 1})
            )
        else:
            logging.info(f'existing doc {dest_path}')
            document = await RetrievedDocument.find_one(
                RetrievedDocument.checksum == checksum
            )

        url = download.request.url
        metadata = await pdfinfo(temp_path)
        text = await pdftotext(temp_path)
        dates = extract_dates(text)
        effective_date = select_effective_date(dates)
        title = self.select_title(metadata, url)
        document_type, confidence = classify_doc_type(text)
        lang_code = detect_lang(text)
        
        now = datetime.now()
        datelist = list(dates.keys())
        datelist.sort()

        if document:
            updates = UpdateRetrievedDocument(
                context_metadata=download.metadata.dict(),
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
                context_metadata=download.metadata.dict(),
                metadata=metadata,
                base_url=base_url.url,
                lang_code=lang_code,
            )
            await create_and_log(self.logger, await self.get_user(), document)

        await self.scrape_task.update(Push({SiteScrapeTask.retrieved_document_ids: document.id}))

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

    def active_base_urls(self):
        return [url for url in self.site.base_urls if url.status == "ACTIVE"]

    def url_filter(self, url):
        return self.unqiue_url(url) and self.valid_scheme(url)

    async def run_scrape(self):

        # TODO interactive -> playwright
        # TODO non-interactive -> beautifulsoup

        # driver has 'main context'; abstraction to 'nav, find, collect';
        # nav, find, collect vary by lib & strategy
        async with PlaywrightDirectDownload(browser=self.browser, proxy=None) as driver:
            strategy = DirectDownloadStategy(
                config=self.site.scrape_method_configuration,
                driver=driver
            )
            
            for base_url in self.active_base_urls():
                
                downloads = await strategy.execute(base_url.url)
                
                if len(downloads) == 0:
                    raise NoDocsCollectedException("No documents collected.")

                filtered = filter(lambda download: self.url_filter(download.request.url), downloads)                
                
                tasks = []
                for download in filtered:
                    await self.scrape_task.update(
                        Inc({SiteScrapeTask.links_found: 1})
                    )

                    tasks.append(asyncio.create_task(self.try_download(download, base_url)))

                try:
                    await asyncio.gather(self.watch_for_cancel(tasks), *tasks)
                except asyncio.exceptions.CancelledError:
                    pass
                
