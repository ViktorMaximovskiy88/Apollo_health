import asyncio
import logging
from datetime import datetime
from turtle import down
from async_lru import alru_cache
from beanie.odm.operators.update.array import Push
from beanie.odm.operators.update.general import Inc
from urllib.parse import urlparse
from backend.common.models.proxy import Proxy
from backend.common.models.site import Site
from backend.common.models.document import RetrievedDocument, UpdateRetrievedDocument
from backend.common.models.site_scrape_task import SiteScrapeTask
from playwright.async_api import Browser, ProxySettings
from backend.common.models.user import User
from backend.scrapeworker.common.proxy import convert_proxies_to_proxy_settings
from backend.app.utils.logger import Logger, create_and_log, update_and_log_diff
from backend.common.storage.client import DocumentStorageClient
from backend.scrapeworker.common.exceptions import (
    NoDocsCollectedException,
    CanceledTaskException,
)

from backend.scrapeworker.common.models import Download
from backend.scrapeworker.drivers.playwright.direct_download import (
    PlaywrightDirectDownload,
)
from backend.scrapeworker.drivers.playwright.asp_web_form import PlaywrightAspWebForm
from backend.scrapeworker.drivers.playwright.word_press_ajax import (
    PlaywrightWordPressAjax,
)

from backend.scrapeworker.strategies.direct_download import DirectDownloadStategy
from backend.scrapeworker.strategies.asp_web_form import AspWebFormStrategy
from backend.scrapeworker.strategies.word_press_ajax import (
    PlaywrightWordPressAjaxStrategy,
)

from backend.scrapeworker.common.downloader.aiohttp_client import AioDownloader
from backend.common.core.enums import Status
from backend.scrapeworker.common.file_metadata import pdf


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
    async def get_proxies(self) -> list[Proxy]:
        proxies = await Proxy.find_all().to_list()
        proxy_exclusions = self.site.scrape_method_configuration.proxy_exclusions
        valid_proxies = [proxy for proxy in proxies if proxy.id not in proxy_exclusions]
        return valid_proxies

    def valid_scheme(self, url):
        parsed = urlparse(url)
        return parsed.scheme in ["https", "http"]  # mailto, tel, etc

    def unqiue_url(self, url):
        # skip if we've already seen this url
        if url in self.seen_urls:
            return False
        self.seen_urls.add(url)
        return True

    async def attempt_download(self, download: Download, base_url):
        proxies = await self.get_proxies()

        async for (temp_path, checksum, file_ext) in self.downloader.download(
            download, proxies
        ):
            await self.scrape_task.update(Inc({SiteScrapeTask.documents_found: 1}))

            dest_path = f"{checksum}.{file_ext}"
            document = None

            # write to our object store (s3/minio)
            if not self.doc_client.document_exists(dest_path):
                logging.info(f"new doc {dest_path}")
                self.doc_client.write_document(dest_path, temp_path)
                await self.scrape_task.update(
                    Inc({SiteScrapeTask.new_documents_found: 1})
                )
            else:
                logging.info(f"existing doc {dest_path}")
                document = await RetrievedDocument.find_one(
                    RetrievedDocument.checksum == checksum
                )

            # parse collected doc
            # if PDF
            parsed = await pdf.parse_metadata(temp_path, download.request.url)

            # if docx
            # parsed = await docx.parse_metadata(temp_path, download.request.url)

            # update our doc in mongo
            now = datetime.now()
            datelist = list(parsed["dates"].keys())
            datelist.sort()

            if document:
                updates = UpdateRetrievedDocument(
                    context_metadata=download.metadata.dict(),
                    doc_type_confidence=parsed["confidence"],
                    document_type=parsed["document_type"],
                    effective_date=parsed["effective_date"],
                    identified_dates=datelist,
                    lang_code=parsed["lang_code"],
                    last_seen=now,
                    metadata=parsed["metadata"],
                    name=parsed["title"],
                    scrape_task_id=self.scrape_task.id,
                )
                await update_and_log_diff(
                    self.logger, await self.get_user(), document, updates
                )
            else:
                document = RetrievedDocument(
                    base_url=base_url.url,
                    checksum=checksum,
                    collection_time=now,
                    context_metadata=download.metadata.dict(),
                    doc_type_confidence=parsed["confidence"],
                    document_type=parsed["document_type"],
                    effective_date=parsed["effective_date"],
                    identified_dates=datelist,
                    lang_code=parsed["lang_code"],
                    last_seen=now,
                    metadata=parsed["metadata"],
                    name=parsed["title"],
                    scrape_task_id=self.scrape_task.id,
                    site_id=self.site.id,
                    url=download.request.url,
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

    def active_base_urls(self):
        return [url for url in self.site.base_urls if url.status == "ACTIVE"]

    def url_filter(self, url):
        return self.unqiue_url(url) and self.valid_scheme(url)

    async def try_direct_download_playwright(self):
        async with PlaywrightDirectDownload(browser=self.browser, proxy=None) as driver:
            strategy = DirectDownloadStategy(
                config=self.site.scrape_method_configuration, driver=driver
            )

            valid_strategy = False
            for base_url in self.active_base_urls():
                elements, downloads = await strategy.execute(base_url.url)
                valid_strategy = len(elements) > 0 and len(downloads) > 0

            # if len(downloads) == 0:
            #     pass
            # instead of raising here, indicate in logs that we found nadda for this strat
            # raise NoDocsCollectedException("No documents collected.")

            if valid_strategy:
                await self.process_downloads(base_url, downloads, elements)

            return valid_strategy

    async def try_asp_web_form_playwright(self):
        async with PlaywrightAspWebForm(browser=self.browser, proxy=None) as driver:
            strategy = AspWebFormStrategy(
                config=self.site.scrape_method_configuration, driver=driver
            )

            valid_strategy = False
            for base_url in self.active_base_urls():
                elements, downloads = await strategy.execute(base_url.url)
                valid_strategy = len(elements) > 0 and len(downloads) > 0

            # if len(downloads) == 0:
            #     pass
            # instead of raising here, indicate in logs that we found nadda for this strat
            # raise NoDocsCollectedException("No documents collected.")

            if valid_strategy:
                await self.process_downloads(base_url, downloads, elements)

            return valid_strategy

    async def try_word_press_ajax_playwright(self):
        async with PlaywrightWordPressAjax(browser=self.browser, proxy=None) as driver:
            strategy = PlaywrightWordPressAjaxStrategy(
                config=self.site.scrape_method_configuration, driver=driver
            )

            valid_strategy = False
            for base_url in self.active_base_urls():
                elements, downloads = await strategy.execute(base_url.url)
                valid_strategy = len(elements) > 0 and len(downloads) > 0

            # if len(downloads) == 0:
            #     pass
            # instead of raising here, indicate in logs that we found nadda for this strat
            # raise NoDocsCollectedException("No documents collected.")

            if valid_strategy:
                await self.process_downloads(base_url, downloads, elements)

            return valid_strategy

    async def process_downloads(self, base_url, downloads, elements):
        filtered = filter(
            lambda download: self.url_filter(download.request.url), downloads
        )

        tasks = []
        for download in filtered:
            await self.scrape_task.update(Inc({SiteScrapeTask.links_found: 1}))
            tasks.append(asyncio.create_task(self.attempt_download(download, base_url)))

        try:
            await asyncio.gather(self.watch_for_cancel(tasks), *tasks)
        except asyncio.exceptions.CancelledError:
            pass

    # main worker ...
    async def run_scrape(self):

        # can try all and update config
        # can read from human set config
        # can do w/e we want to pick strats without waste

        # found_direct_download = await self.try_direct_download_playwright()
        # found_asp_web_form = await self.try_asp_web_form_playwright()
        found_word_press_ajax = await self.try_word_press_ajax_playwright()
