import asyncio
import re
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from random import shuffle
from typing import Any, AsyncGenerator, Callable, Coroutine
from urllib.parse import urlparse

from async_lru import alru_cache
from beanie.odm.operators.update.general import Inc, Set
from playwright.async_api import BrowserContext, Dialog, Page, ProxySettings
from playwright.async_api import Response as PlaywrightResponse
from playwright_stealth import stealth_async
from tenacity._asyncio import AsyncRetrying
from tenacity.stop import stop_after_attempt
from tenacity.wait import wait_random_exponential

from backend.app.utils.logger import Logger, create_and_log
from backend.common.core.enums import TaskStatus
from backend.common.core.log import logging
from backend.common.models.doc_document import DocDocument
from backend.common.models.document import (
    RetrievedDocument,
    RetrievedDocumentLocation,
    UpdateRetrievedDocument,
)
from backend.common.models.link_task_log import (
    FileMetadata,
    InvalidResponse,
    LinkBaseTask,
    LinkRetrievedTask,
    ValidResponse,
    link_retrieved_task_from_download,
)
from backend.common.models.proxy import Proxy
from backend.common.models.shared import DocDocumentLocation
from backend.common.models.site import Site
from backend.common.models.site_scrape_task import SiteScrapeTask
from backend.common.models.user import User
from backend.common.storage.client import DocumentStorageClient
from backend.common.storage.text_handler import TextHandler
from backend.scrapeworker.common.aio_downloader import AioDownloader
from backend.scrapeworker.common.exceptions import CanceledTaskException, NoDocsCollectedException
from backend.scrapeworker.common.models import DownloadContext, Metadata, Request
from backend.scrapeworker.common.proxy import convert_proxies_to_proxy_settings
from backend.scrapeworker.common.utils import get_extension_from_path_like
from backend.scrapeworker.file_parsers import parse_by_type
from backend.scrapeworker.playbook import ScrapePlaybook
from backend.scrapeworker.scrapers import scrapers
from backend.scrapeworker.scrapers.follow_link import FollowLinkScraper

log = logging.getLogger(__name__)


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
        get_browser_context: Callable[[ProxySettings | None], Coroutine[Any, Any, BrowserContext]],
        scrape_task: SiteScrapeTask,
        site: Site,
    ) -> None:
        _log = logging.getLogger(str(scrape_task.id)[:8])
        self.playwright = playwright
        self.get_browser_context = get_browser_context
        self.scrape_task = scrape_task
        self.site = site
        self.seen_urls = set()
        self.doc_client = DocumentStorageClient()
        self.text_handler = TextHandler()
        self.downloader = AioDownloader(_log)
        self.playbook = ScrapePlaybook(self.site.playbook)
        self.logger = Logger()
        self.log = _log

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
        key = f"{url}{filename}" if filename else url
        if key in self.seen_urls:
            return False
        self.log.info(f"unseen target -> {key}")
        self.seen_urls.add(key)
        return True

    async def update_doc_document(self, retrieved_document: RetrievedDocument):
        doc_document = await DocDocument.find_one(
            DocDocument.retrieved_document_id == retrieved_document.id
        )
        if doc_document:
            log.debug(f"doc doc update -> {doc_document.id}")
            rt_doc_location = self.get_site_location(self.site.id, retrieved_document)
            location = self.get_site_location(self.site.id, doc_document)

            if location:
                location.last_collected_date = rt_doc_location.last_collected_date
            else:
                doc_document.locations.append(DocDocumentLocation(**rt_doc_location.dict()))

            # Can be removed after text added to older docs
            doc_document.text_checksum = retrieved_document.text_checksum

            await doc_document.save()
        else:
            await self.create_doc_document(retrieved_document)

    async def create_doc_document(self, retrieved_document: RetrievedDocument):

        doc_document = DocDocument(
            retrieved_document_id=retrieved_document.id,  # type: ignore
            name=retrieved_document.name,
            checksum=retrieved_document.checksum,
            text_checksum=retrieved_document.text_checksum,
            document_type=retrieved_document.document_type,
            doc_type_confidence=retrieved_document.doc_type_confidence,
            end_date=retrieved_document.end_date,
            effective_date=retrieved_document.effective_date,
            last_updated_date=retrieved_document.last_updated_date,
            last_reviewed_date=retrieved_document.last_reviewed_date,
            next_review_date=retrieved_document.next_review_date,
            next_update_date=retrieved_document.next_update_date,
            published_date=retrieved_document.published_date,
            lang_code=retrieved_document.lang_code,
            therapy_tags=retrieved_document.therapy_tags,
            indication_tags=retrieved_document.indication_tags,
            file_extension=retrieved_document.file_extension,
            identified_dates=retrieved_document.identified_dates,
            locations=retrieved_document.locations,
        )

        doc_document.set_computed_values()

        await create_and_log(self.logger, await self.get_user(), doc_document)

    def set_doc_name(self, parsed_content: dict, download: DownloadContext):
        self.log.info(
            f"title='{parsed_content['title']}' link_text='{download.metadata.link_text}' file_name='{download.file_name}' request_url='{download.request.url}'"  # noqa
        )
        return (
            parsed_content["title"]
            or download.metadata.link_text
            or download.file_name
            or download.request.url
        )

    # TODO we temporarily update allthethings. as our code matures, this likely dies
    async def update_retrieved_document(
        self,
        document: RetrievedDocument,
        download: DownloadContext,
        parsed_content: dict,
    ) -> UpdateRetrievedDocument:
        now = datetime.now(tz=timezone.utc)
        name = self.set_doc_name(parsed_content, download)

        location = document.get_site_location(self.site.id)

        if location:
            location.context_metadata = download.metadata.dict()
            location.last_collected_date = now
        else:
            document.locations.append(
                RetrievedDocumentLocation(
                    base_url=download.metadata.base_url,
                    first_collected_date=now,
                    last_collected_date=now,
                    site_id=self.site.id,
                    url=download.request.url,
                    context_metadata=download.metadata.dict(),
                    link_text=download.metadata.link_text,
                )
            )

        updated_doc = UpdateRetrievedDocument(
            doc_type_confidence=parsed_content["confidence"],
            document_type=parsed_content["document_type"],
            effective_date=parsed_content["effective_date"],
            end_date=parsed_content["end_date"],
            last_updated_date=parsed_content["last_updated_date"],
            last_reviewed_date=parsed_content["last_reviewed_date"],
            next_review_date=parsed_content["next_review_date"],
            next_update_date=parsed_content["next_update_date"],
            published_date=parsed_content["published_date"],
            identified_dates=parsed_content["identified_dates"],
            lang_code=parsed_content["lang_code"],
            therapy_tags=parsed_content["therapy_tags"],
            indication_tags=parsed_content["indication_tags"],
            metadata=parsed_content["metadata"],
            name=name,
            text_checksum=document.text_checksum,
            locations=document.locations,
        )

        await document.update(Set(updated_doc.dict(exclude_unset=True)))
        return updated_doc

    async def attempt_download(self, download: DownloadContext):

        url = download.request.url
        proxies = await self.get_proxy_settings()
        link_retrieved_task: LinkRetrievedTask = link_retrieved_task_from_download(
            download, self.scrape_task
        )

        async for (temp_path, checksum) in self.downloader.try_download_to_tempfile(
            download, proxies
        ):
            # TODO temp until we undo download context
            link_retrieved_task.valid_response = download.valid_response
            link_retrieved_task.invalid_responses = download.invalid_responses

            # log response error
            if not (temp_path and checksum):
                self.log.warn("Received an unexpected html response")
                await link_retrieved_task.save()
                continue

            # TODO can we separate the concept of extensions to scrape on
            # and ext we expect to download? for now just html
            if (
                download.file_extension == "html"
                and "html" not in self.site.scrape_method_configuration.document_extensions
            ):
                self.log.warn("Received an unexpected html response")
                await link_retrieved_task.save()
                continue

            link_retrieved_task.file_metadata = FileMetadata(checksum=checksum, **download.dict())

            # log no file parser found error
            parsed_content = await parse_by_type(
                temp_path,
                download,
                self.site.scrape_method_configuration.focus_therapy_configs,
            )
            if parsed_content is None:
                await link_retrieved_task.save()
                self.log.info(f"{download.request.url} {download.file_extension} cannot be parsed")
                # prob not continue anymore...
                continue

            document = None
            dest_path = f"{checksum}.{download.file_extension}"

            self.log.info(f"dest_path={dest_path} temp_path={temp_path}")

            if not self.doc_client.object_exists(dest_path):
                self.doc_client.write_object(dest_path, temp_path, download.mimetype)
                await self.scrape_task.update(Inc({SiteScrapeTask.new_documents_found: 1}))

            # TODO i think this needs to not live here... a lambda to do the 'preview' thing
            # right now opt-in to it
            if (
                download.file_extension == "html"
                and "html" in self.site.scrape_method_configuration.document_extensions
            ):
                async with self.playwright_context(url) as (page, _context):
                    dest_path = f"{checksum}.{download.file_extension}.pdf"
                    await page.goto(download.request.url, wait_until="domcontentloaded")
                    pdf_bytes = await page.pdf(display_header_footer=False, print_background=True)
                    self.doc_client.write_object_mem(relative_key=dest_path, object=pdf_bytes)

            document = await RetrievedDocument.find_one(RetrievedDocument.checksum == checksum)

            if document:
                self.log.info("updating doc")

                if document.text_checksum is None:  # Can be removed after text added to older docs
                    text_checksum = await self.text_handler.save_text(parsed_content["text"])
                    document.text_checksum = text_checksum

                await self.update_retrieved_document(
                    document=document,
                    download=download,
                    parsed_content=parsed_content,
                )

                await self.update_doc_document(document)

            else:
                self.log.info("creating doc")
                now = datetime.now(tz=timezone.utc)
                name = self.set_doc_name(parsed_content, download)
                text_checksum = await self.text_handler.save_text(parsed_content["text"])

                document = RetrievedDocument(
                    checksum=checksum,
                    text_checksum=text_checksum,
                    doc_type_confidence=parsed_content["confidence"],
                    document_type=parsed_content["document_type"],
                    effective_date=parsed_content["effective_date"],
                    end_date=parsed_content["end_date"],
                    last_updated_date=parsed_content["last_updated_date"],
                    last_reviewed_date=parsed_content["last_reviewed_date"],
                    next_review_date=parsed_content["next_review_date"],
                    next_update_date=parsed_content["next_update_date"],
                    published_date=parsed_content["published_date"],
                    file_extension=download.file_extension,
                    content_type=download.content_type,
                    identified_dates=parsed_content["identified_dates"],
                    lang_code=parsed_content["lang_code"],
                    metadata=parsed_content["metadata"],
                    name=name,
                    therapy_tags=parsed_content["therapy_tags"],
                    indication_tags=parsed_content["indication_tags"],
                    locations=[
                        RetrievedDocumentLocation(
                            base_url=download.metadata.base_url,
                            first_collected_date=now,
                            last_collected_date=now,
                            site_id=self.site.id,
                            url=url,
                            context_metadata=download.metadata.dict(),
                            link_text=download.metadata.link_text,
                        )
                    ],
                )

                await create_and_log(self.logger, await self.get_user(), document)
                await self.create_doc_document(document)

            link_retrieved_task.retrieved_document_id = document.id

            await asyncio.gather(
                self.scrape_task.update(
                    {
                        "$inc": {"documents_found": 1},
                        "$push": {"retrieved_document_ids": document.id},
                    }
                ),
                link_retrieved_task.save(),
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
            await asyncio.sleep(5)

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
        async for attempt in AsyncRetrying(
            reraise=True,
            stop=stop_after_attempt(3 * n_proxies),
            wait=wait_random_exponential(multiplier=1, max=60),
        ):
            i = attempt.retry_state.attempt_number - 1
            proxy, proxy_setting = proxy_settings[i % n_proxies]
            self.log.info(
                f"{i} Trying proxy {proxy and proxy.name} - {proxy_setting and proxy_setting.get('server')}"  # noqa
            )
            yield attempt, proxy_setting

    async def wait_for_desired_content(self, page: Page):
        if len(self.site.scrape_method_configuration.wait_for) == 0:
            return

        selector = ", ".join(
            f":text('{wf}')" for wf in self.site.scrape_method_configuration.wait_for
        )

        await page.locator(selector).first.wait_for()

    @asynccontextmanager
    async def playwright_context(
        self, url: str
    ) -> AsyncGenerator[tuple[Page, BrowserContext], None]:
        self.log.info(f"Creating context for {url}")
        context: BrowserContext | None = None
        page: Page | None = None
        response: PlaywrightResponse | None = None

        async def handle_dialog(dialog: Dialog):
            await dialog.accept()

        link_base_task: LinkBaseTask = LinkBaseTask(
            base_url=url,
            site_id=self.scrape_task.site_id,
            scrape_task_id=self.scrape_task.id,  # type: ignore
        )

        async for attempt, proxy in self.try_each_proxy():
            with attempt:
                context = await self.get_browser_context(proxy)

                page = await context.new_page()
                await stealth_async(page)
                page.on("dialog", handle_dialog)

                self.log.info(f"Awating response for {url}")
                # TODO lets set this timeout lower generally and let exceptions set it higher
                response = await page.goto(url, timeout=15000, wait_until="domcontentloaded")
                self.log.info(f"Received response for {url}")

                proxy_url = proxy.get("server") if proxy else None
                if not response:
                    continue

                if not response.ok:
                    self.log.info(f"Received invalid response for {url}")
                    invalid_response = InvalidResponse(
                        proxy_url=proxy_url,
                        status=response.status,
                        message=response.status_text,
                    )

                    link_base_task.invalid_responses.append(invalid_response)
                    self.log.error(invalid_response)
                    continue

                headers = await response.all_headers()
                link_base_task.valid_response = ValidResponse(
                    proxy_url=proxy_url,
                    status=response.status,
                    content_type=headers.get("content-type"),
                    content_length=int(headers.get("content-length", 0)),
                )

        if not page or not context or not response:
            raise Exception(f"Could not load {url}")

        # this may move further down depending on the level of fail we record;

        await link_base_task.save()
        await self.wait_for_desired_content(page)

        try:
            yield page, context
        except Exception as ex:
            # NOTE this is a big change in our error handling
            self.log.error(ex)
        finally:
            if context:
                await context.close()

    def active_base_urls(self):
        return [url for url in self.site.base_urls if url.status == "ACTIVE"]

    def preprocess_download(self, download: DownloadContext, base_url: str):
        download.metadata.base_url = base_url
        if is_google(download.request.url):
            google_id = get_google_id(download.request.url)
            download.request.url = f"https://drive.google.com/u/0/uc?id={google_id}&export=download"

    async def queue_downloads(self, url: str, base_url: str):
        all_downloads: list[DownloadContext] = []

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

    def should_process_download(self, download: DownloadContext):
        url = download.request.url
        filename = (
            download.response.content_disposition_filename
            if download.response and download.response.content_disposition_filename
            else download.request.filename
        )

        return not self.skip_url(url) and self.url_not_seen(url, filename)

    def is_artifact_file(self, url: str):
        extension = get_extension_from_path_like(url)
        return extension in ["docx", "pdf", "xlsx"]

    async def run_scrape(self):
        all_downloads: list[DownloadContext] = []
        base_urls: list[str] = [base_url.url for base_url in self.active_base_urls()]

        # lets log this at runtime for debuggability
        await self.scrape_task.update(
            {"$set": {"scrape_method_configuration": self.site.scrape_method_configuration}}
        )

        for url in base_urls:
            # skip the parse step and download
            self.log.info(f"Run scrape for {url}")

            if self.is_artifact_file(url):
                self.log.info(f"Skip scrape & queue download for {url}")
                download = DownloadContext(
                    request=Request(url=url), metadata=Metadata(base_url=url)
                )
                all_downloads.append(download)
                continue

            all_downloads += await self.queue_downloads(url, url)
            if self.site.scrape_method_configuration.follow_links:
                self.log.info(f"Follow links for {url}")
                for nested_url in await self.follow_links(url):
                    all_downloads += await self.queue_downloads(nested_url, base_url=url)

        tasks = []
        for download in all_downloads:
            if self.should_process_download(download):
                await self.scrape_task.update(Inc({SiteScrapeTask.links_found: 1}))
                tasks.append(self.attempt_download(download))
            else:
                self.log.info(f"Skip download {download.request.url}")

        await self.wait_for_completion_or_cancel(tasks)
        await self.downloader.close()

        if not self.scrape_task.documents_found:
            raise NoDocsCollectedException("No documents collected.")
