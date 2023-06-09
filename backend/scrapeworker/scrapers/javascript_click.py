import asyncio
import logging
import os
from functools import cached_property

from playwright.async_api import Download, ElementHandle, Page
from playwright.async_api import Response as PageResponse
from playwright.async_api import TimeoutError as PlaywrightTimeout

from backend.scrapeworker.common.models import DownloadContext, Metadata, Request, Response
from backend.scrapeworker.common.selectors import to_xpath
from backend.scrapeworker.scrapers.playwright_base_scraper import PlaywrightBaseScraper


class JavascriptClick(PlaywrightBaseScraper):

    type: str = "Javascript"
    requests: list[Request | None] = []
    metadatas: list[Metadata] = []
    downloads: list[DownloadContext] = []
    links_found: int = 0
    last_metadata_index: int = 0

    @cached_property
    def css_selector(self) -> str | None:
        css_selectors = []
        return ",".join(css_selectors)

    @cached_property
    def xpath_selector(self) -> str:
        selectors = []
        for attr_selector in self.config.attr_selectors:
            if not attr_selector.resource_address:
                selectors.append(to_xpath(attr_selector))
        selector_string = "|".join(selectors)
        self.log.info(selector_string)
        return selector_string

    # Handle special json responses which contain links to downloadable media.
    async def handle_json(self, response: PageResponse) -> DownloadContext | None:
        if not response.headers.get("content-type", False):
            content_type = None
        else:
            content_type = response.headers["content-type"]
        try:
            parsed = await response.json()
            # Reset content_type to headers returned by json response.
            content_type = response.headers["content-type"]
        except Exception:
            self.log.debug("no json response")
            return None
        # Handle contentful json field field.
        # content_type == "application/vnd.contentful.delivery.v1+json"
        if "fields" in parsed and "file" in parsed["fields"]:  # Contentful
            self.log.debug(f"follow json file field {content_type}")
            file_field = parsed["fields"]["file"]
            return DownloadContext(
                content_type=file_field["contentType"],
                request=Request(
                    url=f'https:{file_field["url"]}',
                    filename=file_field["fileName"],
                ),
            )
        elif "entry" in parsed and "content" in parsed["entry"]:  # WPS
            content_field = parsed["entry"]["content"]["resourceUri"]
            return DownloadContext(
                content_type=content_field["type"],
                request=Request(
                    url=f'https://{self.parsed_url.netloc}{content_field["value"]}',
                    filename=parsed["entry"]["title"]["value"],
                ),
            )
        return None

    async def execute(self) -> list[DownloadContext]:
        downloads: list[DownloadContext] = []
        link_handle: ElementHandle
        page_process_queue: list[asyncio.Future[None]] = []

        async def postprocess_response(response: PageResponse) -> None:
            accepted_types = [
                "application/pdf",
                "application/vnd.ms-excel",
                "application/msword",
            ]
            try:
                await response.finished()
                content_type: str | None = None
                if "content-type" in response.headers:
                    content_type = response.headers["content-type"]
                download = await self.handle_json(response)
                cookies = await self.context.cookies(response.url)
                if (
                    isinstance(download, DownloadContext)
                    and download.content_type in accepted_types
                ):
                    download.request.cookies = cookies
                    download.metadata = await self.extract_metadata(link_handle)
                    downloads.append(download)
                elif content_type in accepted_types:
                    logging.info(f"Direct Download result: {content_type} - {response.url}")
                    download = DownloadContext(
                        response=Response(content_type=content_type, status=response.status),
                        request=Request(url=response.url, cookies=cookies),
                    )
                    download.metadata = await self.extract_metadata(link_handle)
                    downloads.append(download)
                else:
                    self.log.debug(f"Unknown json response: {response.headers}")
                    return None
            except Exception:
                logging.error("exception", exc_info=True)

        async def postprocess_download(download: Download) -> None:
            accepted_types = [".pdf", ".xls", ".xlsx", ".doc", ".docx"]
            try:
                # Response may not always have content-type header.
                # Use filename ext instead.
                # suggested_filename='PriorAuthorization.pdf'
                filename, file_extension = os.path.splitext(download.suggested_filename)
                if file_extension in accepted_types:
                    self.log.debug(
                        f"javascript click -> direct download: {filename}.{file_extension}"
                    )
                    cookies = await self.context.cookies(download.url)
                    download_context = DownloadContext(
                        response=Response(content_type=None),
                        request=Request(url=download.url, cookies=cookies),
                    )
                    download_context.metadata = await self.extract_metadata(link_handle)
                    downloads.append(download_context)
                else:
                    self.log.debug(f"unknown download extension: {file_extension}")
                    return None
            except Exception:
                logging.error("exception", exc_info=True)

        async def cleanup_page(page: Page):
            page.on("download", postprocess_download)
            cleanup_future = asyncio.Future()
            page_process_queue.append(cleanup_future)
            await asyncio.sleep(10)  # allow processes to complete
            await page.close()
            cleanup_future.set_result(None)

        self.context.on("page", cleanup_page)
        # Handle onclick json response where the json has link to pdf.
        self.context.on("response", postprocess_response)
        # Handle onclick download directly to pdf rather than response.
        self.page.on("download", postprocess_download)

        xpath_locator = self.page.locator(self.xpath_selector)
        xpath_locator_count = await xpath_locator.count()
        for index in range(0, xpath_locator_count):
            try:
                link_handle = await xpath_locator.nth(index).element_handle(timeout=1000)
                await link_handle.click(timeout=10000, button="middle")
                await asyncio.sleep(0.25)
            except PlaywrightTimeout as ex:
                # If Playwright Timeout, we likely haven't nav'd away
                self.log.error(ex, exc_info=True)
            except Exception as ex:
                self.log.error(ex, exc_info=True, stack_info=True)
                await self.nav_to_base()

        await asyncio.gather(*page_process_queue)  # be sure all downloads complete
        return downloads
