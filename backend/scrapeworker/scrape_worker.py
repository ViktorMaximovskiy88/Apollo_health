import asyncio
from contextlib import asynccontextmanager
from random import shuffle
from typing import AsyncGenerator, Coroutine
from urllib.parse import urlparse

from async_lru import alru_cache
from beanie.odm.operators.update.general import Inc
from playwright.async_api import Browser, BrowserContext, Cookie, Dialog, Page, ProxySettings
from playwright.async_api import Response as PlaywrightResponse
from playwright_stealth import stealth_async
from tenacity._asyncio import AsyncRetrying
from tenacity.stop import stop_after_attempt
from tenacity.wait import wait_random_exponential

from backend.common.core.enums import TaskStatus
from backend.common.core.log import logging
from backend.common.models.doc_document import DocDocument, IndicationTag, TherapyTag
from backend.common.models.document import RetrievedDocument
from backend.common.models.link_task_log import (
    FileMetadata,
    InvalidResponse,
    LinkBaseTask,
    LinkRetrievedTask,
    ValidResponse,
    link_retrieved_task_from_download,
)
from backend.common.models.proxy import Proxy
from backend.common.models.site import Site
from backend.common.models.site_scrape_task import SiteScrapeTask
from backend.common.services.doc_lifecycle.doc_lifecycle import DocLifecycleService
from backend.common.services.doc_lifecycle.hooks import ChangeInfo, doc_document_save_hook
from backend.common.services.lineage.lineage import LineageService
from backend.common.storage.client import DocumentStorageClient
from backend.common.storage.hash import hash_full_text
from backend.common.storage.text_handler import TextHandler
from backend.scrapeworker.common.aio_downloader import AioDownloader, default_headers
from backend.scrapeworker.common.exceptions import CanceledTaskException, NoDocsCollectedException
from backend.scrapeworker.common.models import DownloadContext, Metadata, Request
from backend.scrapeworker.common.proxy import convert_proxies_to_proxy_settings
from backend.scrapeworker.common.update_documents import DocumentUpdater
from backend.scrapeworker.common.utils import get_extension_from_path_like
from backend.scrapeworker.file_parsers import parse_by_type
from backend.scrapeworker.playbook import ScrapePlaybook
from backend.scrapeworker.scrapers import ScrapeHandler
from backend.scrapeworker.scrapers.follow_link import FollowLinkScraper
from backend.scrapeworker.search_crawler import SearchableCrawler

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class ScrapeWorker:
    def __init__(
        self,
        playwright,
        browser: Browser,
        scrape_task: SiteScrapeTask,
        site: Site,
    ) -> None:
        _log = logging.getLogger(str(scrape_task.id))
        self.playwright = playwright
        self.browser = browser
        self.scrape_task = scrape_task
        self.site = site
        self.seen_urls = set()
        self.seen_hashes = set()
        self.doc_client = DocumentStorageClient()
        self.text_handler = TextHandler()
        self.downloader = AioDownloader(self.doc_client, _log)
        self.playbook = ScrapePlaybook(self.site.playbook)
        self.search_crawler = SearchableCrawler(
            config=self.site.scrape_method_configuration, log=_log
        )
        self.doc_updater = DocumentUpdater(_log, scrape_task, site)
        self.lineage_service = LineageService(logger=_log)
        self.doc_lifecycle_service = DocLifecycleService(logger=_log)
        self.new_document_pairs: list[tuple[RetrievedDocument, DocDocument]] = []
        self.log = _log

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

    def file_hash_not_seen(self, hash: str | None):
        # skip if we've already seen this filehash
        if not hash or hash in self.seen_hashes:
            return False
        self.log.info(f"unseen target -> {hash}")
        self.seen_hashes.add(hash)
        return True

    def get_updated_tags(
        self,
        existing_doc: RetrievedDocument,
        therapy_tags: list[TherapyTag],
        indication_tags: list[IndicationTag],
    ):
        ###
        # Return lists of new therapy and indication tags compared against existing tags
        # Checks tag code and tag page for equality, ignoring changes in other attributes
        ###
        therapy_tags_hash: dict[str, list[int]] = {}
        indicate_tags_hash: dict[int, list[int]] = {}
        for tag in existing_doc.therapy_tags:
            if tag.code in therapy_tags_hash:
                therapy_tags_hash[tag.code].append(tag.page)
            else:
                therapy_tags_hash[tag.code] = [tag.page]

        for tag in existing_doc.indication_tags:
            if tag.code in indicate_tags_hash:
                indicate_tags_hash[tag.code].append(tag.page)
            else:
                indicate_tags_hash[tag.code] = [tag.page]

        new_therapy_tags = [
            tag
            for tag in therapy_tags
            if tag.code not in therapy_tags_hash or tag.page not in therapy_tags_hash[tag.code]
        ]
        new_indicate_tags = [
            tag
            for tag in indication_tags
            if tag.code not in indicate_tags_hash or tag.page not in indicate_tags_hash[tag.code]
        ]
        return new_therapy_tags, new_indicate_tags

    async def attempt_download(self, download: DownloadContext):
        url = download.request.url
        proxies = await self.get_proxy_settings()
        link_retrieved_task: LinkRetrievedTask = link_retrieved_task_from_download(
            download, self.scrape_task
        )
        # prob our fail
        async for (temp_path, checksum) in self.downloader.try_download_to_tempfile(
            download, proxies
        ):

            # TODO temp until we undo download context
            link_retrieved_task.valid_response = download.valid_response
            link_retrieved_task.invalid_responses = download.invalid_responses

            # log response error
            if not (temp_path and checksum):
                await link_retrieved_task.save()
                break

            # TODO can we separate the concept of extensions to scrape on
            # and ext we expect to download? for now just html
            if download.file_extension == "html" and (
                "html" not in self.site.scrape_method_configuration.document_extensions
                and self.site.scrape_method != "HtmlScrape"
            ):
                self.log.error("Received an unexpected html response")
                await link_retrieved_task.save()
                break

            link_retrieved_task.file_metadata = FileMetadata(checksum=checksum, **download.dict())

            parsed_content = await parse_by_type(
                temp_path,
                download,
                focus_config=self.site.scrape_method_configuration.focus_section_configs,
                scrape_method_config=self.site.scrape_method_configuration,
            )

            if parsed_content is None:
                await link_retrieved_task.save()
                self.log.error(f"{download.request.url} {download.file_extension} cannot be parsed")
                break

            document = None
            dest_path = f"{checksum}.{download.file_extension}"

            if not self.doc_client.object_exists(dest_path):
                self.doc_client.write_object(dest_path, temp_path, download.mimetype)

            if download.file_extension == "html" and (
                "html" in self.site.scrape_method_configuration.document_extensions
                or self.site.scrape_method == "HtmlScrape"
            ):
                target_url = url if not download.direct_scrape else f"file://{temp_path}"
                async with self.playwright_context(target_url, download.request.cookies) as (
                    page,
                    _context,
                ):
                    dest_path = f"{checksum}.{download.file_extension}.pdf"
                    await page.goto(target_url, wait_until="domcontentloaded")
                    pdf_bytes = await page.pdf(display_header_footer=False, print_background=True)
                    self.doc_client.write_object_mem(relative_key=dest_path, object=pdf_bytes)

            if download.file_extension == "html":
                text_checksum = hash_full_text(parsed_content["text"])
                document = await RetrievedDocument.find_one(
                    RetrievedDocument.text_checksum == text_checksum
                )
            else:
                document = await RetrievedDocument.find_one(RetrievedDocument.checksum == checksum)

            if document:
                self.log.info("updating doc")
                if document.text_checksum is None:  # Can be removed after text added to older docs
                    text_checksum = await self.text_handler.save_text(parsed_content["text"])
                    document.text_checksum = text_checksum

                new_therapy_tags, new_indicate_tags = self.get_updated_tags(
                    document,
                    parsed_content["therapy_tags"],
                    parsed_content["indication_tags"],
                )

                await self.doc_updater.update_retrieved_document(
                    document=document,
                    download=download,
                    parsed_content=parsed_content,
                )

                doc_document = await self.doc_updater.update_doc_document(
                    document, new_therapy_tags, new_indicate_tags
                )

            else:
                document = await self.doc_updater.create_retrieved_document(
                    parsed_content, download, checksum, url
                )
                doc_document = await self.doc_updater.create_doc_document(document)
                await self.scrape_task.update(
                    {
                        "$inc": {"new_documents_found": 1},
                        "$push": {"new_retrieved_document_ids": document.id},
                    }
                )
                self.new_document_pairs.append((document, doc_document))

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
        self, url: str, cookies: list[Cookie] = []
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
                context = await self.browser.new_context(
                    extra_http_headers=default_headers,
                    proxy=proxy,  # type: ignore
                    ignore_https_errors=True,
                )
                await context.add_cookies(cookies)  # type: ignore

                page = await context.new_page()
                await stealth_async(page)
                page.on("dialog", handle_dialog)

                self.log.info(f"Awaiting response for {url}")
                base_url_timeout = self.site.scrape_method_configuration.base_url_timeout_ms
                response = await page.goto(
                    url,
                    timeout=base_url_timeout,
                    wait_until="domcontentloaded",
                )
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
            self.log.error(ex, stack_info=True)
        finally:
            if context:
                await context.close()

    def active_base_urls(self):
        return [url for url in self.site.base_urls if url.status == "ACTIVE"]

    async def queue_downloads(self, url: str, base_url: str, cookies: list[Cookie] = []):
        all_downloads: list[DownloadContext] = []

        async with self.playwright_context(url, cookies) as (base_page, context):
            async for (page, playbook_context) in self.playbook.run_playbook(base_page):

                scrape_handler = ScrapeHandler(
                    context=context,
                    page=page,
                    playbook_context=playbook_context,
                    log=self.log,
                    config=self.site.scrape_method_configuration,
                )

                if await self.search_crawler.is_searchable(page):
                    async for code in self.search_crawler.run_searchable(page, playbook_context):
                        await scrape_handler.run_scrapers(
                            url, base_url, all_downloads, {"file_name": code}
                        )
                else:
                    await scrape_handler.run_scrapers(url, base_url, all_downloads)

        return all_downloads

    async def follow_links(self, url) -> tuple[list[str], list[Cookie]]:
        urls: list[str] = []
        page: Page
        context: BrowserContext
        cookies: list[Cookie] = []
        async with self.playwright_context(url) as (page, context):
            crawler = FollowLinkScraper(
                page=page,
                context=context,
                config=self.site.scrape_method_configuration,
                url=url,
            )

            cookies = await context.cookies()
            if await crawler.is_applicable():
                for dl in await crawler.execute():
                    urls.append(dl.request.url)

        return urls, cookies

    def should_process_download(self, download: DownloadContext):
        url = download.request.url
        filename = (
            download.response.content_disposition_filename
            if download.response and download.response.content_disposition_filename
            else download.request.filename
        )

        return (
            not self.skip_url(url) and self.url_not_seen(url, filename)
        ) or self.file_hash_not_seen(download.file_hash)

    def is_artifact_file(self, url: str):
        extension = get_extension_from_path_like(url)
        return extension in ["docx", "pdf", "xlsx"]

    # NOTE: this is the effective entryppoint from main.py
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

            # NOTE if the base url ends in a handled file extension,
            # queue it up for the aiohttp downloader
            if self.is_artifact_file(url):
                self.log.info(f"Skip scrape & queue download for {url}")
                download = DownloadContext(
                    request=Request(url=url), metadata=Metadata(base_url=url)
                )
                all_downloads.append(download)
                continue

            all_downloads += await self.queue_downloads(url, url)
            if self.site.scrape_method_configuration.follow_links:
                self.log.debug(f"Follow links for {url}")
                (links_found, cookies) = await self.follow_links(url)
                for nested_url in links_found:
                    await self.scrape_task.update(Inc({SiteScrapeTask.follow_links_found: 1}))
                    all_downloads += await self.queue_downloads(
                        nested_url, base_url=url, cookies=cookies
                    )

        tasks = []
        for download in all_downloads:
            if self.should_process_download(download):
                await self.scrape_task.update(Inc({SiteScrapeTask.links_found: 1}))
                tasks.append(self.attempt_download(download))
            else:
                self.log.info(f"Skip download {download.request.url}")

        await self.wait_for_completion_or_cancel(tasks)

        doc_ids = [doc.id for (doc, _) in self.new_document_pairs]
        site_id = self.site.id
        await self.lineage_service.process_lineage_for_doc_ids(site_id, doc_ids)  # type: ignore

        doc_doc_ids = [doc.id for (_, doc) in self.new_document_pairs]
        change_info = ChangeInfo(translation_change=True, lineage_change=True)
        async for doc in DocDocument.find(DocDocument.id in doc_doc_ids):
            await doc_document_save_hook(doc, change_info)

        self.site.last_run_documents = self.scrape_task.documents_found
        await self.site.save()

        await self.downloader.close()

        if not self.scrape_task.documents_found:
            raise NoDocsCollectedException("No documents collected.")
