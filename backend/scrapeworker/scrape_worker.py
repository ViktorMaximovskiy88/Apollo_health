import asyncio
import tempfile
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from random import shuffle
from typing import AsyncGenerator
from urllib.parse import urlparse

import aiofiles
import fitz
from async_lru import alru_cache
from beanie.odm.operators.update.general import Inc, Set
from playwright.async_api import Browser, BrowserContext, Cookie, Dialog, Page, ProxySettings
from playwright.async_api import Response as PlaywrightResponse
from playwright_stealth import stealth_async
from tenacity._asyncio import AsyncRetrying
from tenacity.stop import stop_after_attempt
from tenacity.wait import wait_random_exponential

from backend.common.core.enums import ScrapeMethod, TaskStatus
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
from backend.common.services.lineage.core import LineageService
from backend.common.storage.client import DocumentStorageClient
from backend.common.storage.hash import hash_content, hash_full_text
from backend.common.storage.text_handler import TextHandler
from backend.scrapeworker.common.aio_downloader import AioDownloader, default_headers
from backend.scrapeworker.common.exceptions import CanceledTaskException, NoDocsCollectedException
from backend.scrapeworker.common.models import DownloadContext, Metadata, Request
from backend.scrapeworker.common.proxy import convert_proxies_to_proxy_settings
from backend.scrapeworker.common.update_documents import DocumentUpdater
from backend.scrapeworker.common.utils import get_extension_from_path_like, supported_mimetypes
from backend.scrapeworker.file_parsers import get_tags, parse_by_type, pdf
from backend.scrapeworker.playbook import PlaybookException, ScrapePlaybook
from backend.scrapeworker.scrapers import ScrapeHandler
from backend.scrapeworker.scrapers.by_domain.tricare import TricareScraper
from backend.scrapeworker.scrapers.cms.cms_scraper import CMSScrapeController
from backend.scrapeworker.scrapers.follow_link import FollowLinkScraper
from backend.scrapeworker.search_crawler import SearchableCrawler

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


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

    async def html_to_pdf(self, url: str, download: DownloadContext, checksum: str, temp_path: str):
        dest_path = f"{checksum}.{download.file_extension}.pdf"
        if download.direct_scrape:
            async with aiofiles.open(temp_path) as html_file:
                html = await html_file.read()
            story = fitz.Story(html=html)
            page_bounds = fitz.paper_rect("letter")
            content_bounds = page_bounds + (36, 54, -36, -54)  # borders of 0.5 and .75 inches
            with tempfile.NamedTemporaryFile() as pdf_temp:
                writer = fitz.DocumentWriter(pdf_temp)
                more_pages = 1
                while more_pages:
                    current_page = writer.begin_page(page_bounds)
                    more_pages, _ = story.place(content_bounds)
                    story.draw(current_page)
                    writer.end_page()
                writer.close()
                yield pdf_temp.name

                pdf_doc = fitz.Document(pdf_temp)
                pdf_bytes: bytes = pdf_doc.tobytes()  # type: ignore
                self.doc_client.write_object_mem(relative_key=dest_path, object=pdf_bytes)
        else:
            async with self.playwright_context(url, download.request.cookies) as (
                page,
                _context,
            ):
                await page.goto(url, wait_until="domcontentloaded")
                pdf_bytes = await page.pdf(display_header_footer=False, print_background=True)
                with tempfile.NamedTemporaryFile() as pdf_temp:
                    pdf_temp.write(pdf_bytes)
                    yield pdf_temp.name
                self.doc_client.write_object_mem(relative_key=dest_path, object=pdf_bytes)

    def get_updated_tags(
        self,
        existing_doc: DocDocument,
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

    def is_unexpected_html(self, download: DownloadContext):
        return download.file_extension == "html" and (
            "html" not in self.site.scrape_method_configuration.document_extensions
            and (
                self.site.scrape_method != ScrapeMethod.Html
                and self.site.scrape_method != ScrapeMethod.CMS
            )
        )

    async def attempt_download(self, download: DownloadContext, index=0):
        # TODO: This function keeps getting added to.
        # Maybe turn this into a class after our deadlines...
        # This is kinda your 'do thing' or controller; i dunno about _it_ being a class
        url = download.request.url
        proxies = await self.get_proxy_settings()
        link_retrieved_task: LinkRetrievedTask = link_retrieved_task_from_download(
            download, self.scrape_task
        )

        scrape_method_config = self.site.scrape_method_configuration
        async with self.downloader.try_download_to_tempfile(download, proxies) as (
            temp_path,
            checksum,
        ):

            # TODO temp until we undo download context
            link_retrieved_task.valid_response = download.valid_response
            link_retrieved_task.invalid_responses = download.invalid_responses

            # log response error
            if not (temp_path and checksum):
                message = f"Missing required value: temp_path={temp_path} checksum={checksum}"
                self.log.error(message)
                link_retrieved_task.error_message = message
                await link_retrieved_task.save()
                return

            if download.mimetype not in supported_mimetypes:
                message = f"Mimetype not supported. mimetype={download.mimetype}"
                self.log.error(message)
                link_retrieved_task.error_message = message
                await link_retrieved_task.save()
                return

            if self.is_unexpected_html(download):
                message = f"Received an unexpected html response. mimetype={download.mimetype}"
                self.log.error(message)
                link_retrieved_task.error_message = message
                await link_retrieved_task.save()
                return

            link_retrieved_task.file_metadata = FileMetadata(checksum=checksum, **download.dict())

            parsed_content = await parse_by_type(
                temp_path,
                download,
                scrape_method_config=scrape_method_config,
            )

            if parsed_content is None:
                message = f"Cannot parse file. mimetype={download.mimetype} file_extension={download.file_extension}"  # noqa
                self.log.error(message)
                link_retrieved_task.error_message = message
                await link_retrieved_task.save()
                return

            dest_path = f"{checksum}.{download.file_extension}"

            # TODO speak to matt about ocr and this...
            if (
                not parsed_content["text"]
                or len(parsed_content["text"]) == 0
                and download.file_extension != "pdf"
            ):
                message = f"No text detected in file. path={dest_path}"
                self.log.error(message)
                link_retrieved_task.error_message = message
                await link_retrieved_task.save()
                return

            document = None

            text_checksum = hash_full_text(parsed_content["text"])
            parsed_content["content_checksum"] = await hash_content(
                parsed_content["text"], parsed_content["images"]
            )

            document = await RetrievedDocument.find_one(RetrievedDocument.checksum == checksum)
            if not document:
                document = await RetrievedDocument.find_one(
                    RetrievedDocument.text_checksum == text_checksum
                )

            if not document and not self.doc_client.object_exists(dest_path):
                self.doc_client.write_object(dest_path, temp_path, download.mimetype)

            if download.file_extension == "html" and (
                "html" in scrape_method_config.document_extensions
                or self.site.scrape_method == ScrapeMethod.Html
                or self.site.scrape_method == ScrapeMethod.CMS
            ):
                async for pdf_path in self.html_to_pdf(url, download, checksum, temp_path):
                    await pdf.PdfParse(
                        pdf_path,
                        url,
                        link_text=download.metadata.link_text,
                        scrape_method_config=scrape_method_config,
                        download=download,
                    ).update_parsed_content(parsed_content)

            if document:
                self.log.info("updating doc")
                doc_doc = await DocDocument.find_one(
                    DocDocument.retrieved_document_id == document.id
                )
                if not doc_doc:
                    self.log.error(f"DocDocument {document.id} not found")
                    return

                await get_tags(parsed_content, document=doc_doc)
                # TODO this will get axed when the async tasks are ready to schedule
                # Can be removed after text added to older docs
                if document.text_checksum is None and len(parsed_content["text"]) > 0:
                    text_checksum = await self.text_handler.save_text(parsed_content["text"])
                    document.text_checksum = text_checksum

                # in the case where the pdf has no text (aka is an image),
                # set the text checksum to the checksum
                # TODO this will change will our pdf extract image content parsing...
                if len(parsed_content["text"]) == 0 and download.file_extension == "pdf":
                    document.text_checksum = checksum

                new_therapy_tags, new_indicate_tags = self.get_updated_tags(
                    doc_doc,
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
                await get_tags(
                    parsed_content, focus_configs=scrape_method_config.focus_section_configs
                )
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

            await asyncio.wait(
                fs=[
                    self.scrape_task.update(
                        {
                            "$set": {"last_doc_collected": datetime.now(tz=timezone.utc)},
                            "$inc": {"documents_found": 1},
                            "$push": {"retrieved_document_ids": document.id},
                        }
                    ),
                    link_retrieved_task.save(),
                ]
            )

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

        # TODO wait_for_desired_content is for text; lets do custom selectors
        await self.wait_for_desired_content(page)

        try:
            yield page, context
        except PlaybookException as ex:
            raise ex
        except Exception as ex:
            self.log.error(ex, exc_info=ex)
        finally:
            if context:
                await context.close()

    def active_base_urls(self):
        return [url for url in self.site.base_urls if url.status == "ACTIVE"]

    async def queue_downloads(
        self, url: str, base_url: str, cookies: list[Cookie] = [], skip_playbook: bool = False
    ):
        all_downloads: list[DownloadContext] = []

        async with self.playwright_context(url, cookies) as (base_page, context):
            async for (page, playbook_context) in self.playbook.run_playbook(
                base_page, skip_playbook=skip_playbook
            ):
                scrape_handler = ScrapeHandler(
                    context=context,
                    page=page,
                    playbook_context=playbook_context,
                    log=self.log,
                    config=self.site.scrape_method_configuration,
                    scrape_method=self.site.scrape_method,
                )
                if await self.search_crawler.is_searchable(page):
                    async for code in self.search_crawler.run_searchable(page, playbook_context):
                        await scrape_handler.run_scrapers(
                            url, base_url, all_downloads, {"file_name": code, "is_searchable": True}
                        )
                else:
                    await scrape_handler.run_scrapers(url, base_url, all_downloads)

        return all_downloads

    async def follow_links(self, url) -> tuple[set[str], list[Cookie]]:
        urls: set[str] = set()
        page: Page
        context: BrowserContext
        cookies: list[Cookie] = []
        async with self.playwright_context(url) as (base_page, context):
            async for page, _ in self.playbook.run_playbook(base_page):
                crawler = FollowLinkScraper(
                    page=page,
                    context=context,
                    config=self.site.scrape_method_configuration,
                    url=url,
                )

                cookies = await context.cookies()
                if await crawler.is_applicable():
                    async for dl in crawler.execute():
                        urls.add(dl.request.url)

        return urls, cookies

    async def tricare_batch(self, search_terms):
        page: Page
        context: BrowserContext
        downloads = []
        async with self.playwright_context(TricareScraper.base_url) as (page, context):
            scraper = TricareScraper(
                page=page,
                context=context,
                config=self.site.scrape_method_configuration,
                url=TricareScraper.base_url,
                scrape_method=self.site.scrape_method,
                log=self.log,
            )
            downloads += await scraper.execute(search_terms)

        return downloads

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

        # temp batch by letter...
        if self.site.scrape_method == ScrapeMethod.Tricare:
            search_term_buckets, terms = await TricareScraper.get_search_term_buckets()

            await self.scrape_task.update(
                Set({SiteScrapeTask.batch_status.total_pages: len(search_term_buckets)})
            )

            for batch_page, search_terms in enumerate(search_term_buckets):
                batch_key = search_terms[0]
                self.log.info(
                    f"batch_key={batch_key} batch_page={batch_page} search_terms={len(search_terms)}"  # noqa
                )
                await self.scrape_task.update(
                    Set({SiteScrapeTask.batch_status.current_page: batch_page})
                )
                downloads = await self.tricare_batch(search_terms)
                self.log.info(
                    f"terms={len(search_terms)} batch_key={batch_key} downloads={len(downloads)}"
                )
                await self.stop_if_canceled()
                await self.batch_downloads(downloads, 15)

        for url in base_urls:
            # skip the parse step and download
            self.log.info(f"Run scrape for {url}")
            if self.site.scrape_method == ScrapeMethod.CMS:
                self.log.info("Skip scrape & process CMS")
                proxies = await self.get_proxy_settings()
                cms_scraper = CMSScrapeController(
                    doc_types=self.site.scrape_method_configuration.cms_doc_types,
                    downloader=self.downloader,
                    doc_client=self.doc_client,
                    proxies=proxies,
                    log=self.log,
                )
                async for downloads in cms_scraper.batch_execute():
                    self.log.info(f"Queueing {len(downloads)} CMS downloads")
                    all_downloads += downloads
                continue

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
                        nested_url, base_url=url, cookies=cookies, skip_playbook=True
                    )

        download_queue = [
            download for download in all_downloads if self.should_process_download(download)
        ]

        # dont double dip for tricare; TODO will replace this with yield for all
        if self.site.scrape_method != ScrapeMethod.Tricare:
            await self.batch_downloads(download_queue)

        try:
            # doc_ids = [doc.id for (doc, _) in self.new_document_pairs]
            site_id = self.site.id
            # TEMPORARY: lets see how the scrapeworker fares at this (vs our webapp...)
            self.log.info(f"before lineage_service.process_lineage_for_site site_id={site_id}")
            await self.lineage_service.process_lineage_for_site(site_id)  # type: ignore

            doc_doc_ids = [doc.id for (_, doc) in self.new_document_pairs]
            async for doc in DocDocument.find({"_id": {"$in": doc_doc_ids}}):
                change_info = ChangeInfo(
                    translation_change=bool(doc.translation_id),
                    lineage_change=bool(doc.previous_doc_doc_id),
                    document_family_change=bool(doc.document_family_id),
                )
                await doc_document_save_hook(doc, change_info)
            async for doc in DocDocument.find(
                {"locations.site_id": site_id, "_id": {"$nin": doc_doc_ids}}
            ):
                await doc_document_save_hook(doc)
            self.log.info(f"after lineage_service.process_lineage_for_site site_id={site_id}")
        except Exception as ex:
            self.log.error("Lineage error", exc_info=ex)

        self.site.last_run_documents = self.scrape_task.documents_found

        await self.site.save()
        await self.downloader.close()

        if not self.scrape_task.documents_found:
            raise NoDocsCollectedException("No documents collected.")

    async def stop_if_canceled(self):
        result = await SiteScrapeTask.find_one(
            SiteScrapeTask.id == self.scrape_task.id,
            SiteScrapeTask.status == TaskStatus.CANCELING,
        )
        if result:
            raise CanceledTaskException("Task was canceled.")

    async def batch_downloads(self, all_downloads: list, batch_size: int = 20):
        await self.scrape_task.update(Inc({SiteScrapeTask.links_found: len(all_downloads)}))

        batch_index = 0
        while len(all_downloads) > 0:
            downloads = all_downloads[:batch_size]
            del all_downloads[:batch_size]

            tasks = [self.attempt_download(download, index=batch_index) for download in downloads]

            done, pending = await asyncio.wait(fs=tasks)
            self.log.info(f"after wait done={len(done)} pending={len(pending)}")
            batch_index += 1

            await self.stop_if_canceled()
