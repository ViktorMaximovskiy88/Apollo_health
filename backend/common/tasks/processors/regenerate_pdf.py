import logging
import tempfile

import fitz

import backend.common.models.tasks as tasks
from backend.common.models.doc_document import DocDocument
from backend.common.storage.client import DocumentStorageClient
from backend.common.tasks.task_processor import TaskProcessor


class RegeneratePdfProcessor(TaskProcessor):

    dependencies: list[str] = [
        "doc_client",
    ]

    def __init__(
        self,
        doc_client: DocumentStorageClient | None = None,
        logger=logging,
    ) -> None:
        self.logger = logger
        self.doc_client = doc_client or DocumentStorageClient()

    async def exec(self, task: tasks.ContentTask):
        doc_doc: DocDocument | None = await DocDocument.find_one(
            {"_id": task.doc_doc_id},
        )
        if not doc_doc:
            raise Exception(f"cannot find doc_doc with doc_doc {task.doc_doc_id}")

        # Make sure doc has existing html doc already scraped.
        # If the html doc does not exist, you will need to refactor the
        # scraper to support rescraping 1 doc vs the entire site.
        self.doc_client: DocumentStorageClient = DocumentStorageClient()
        if not self.doc_client.object_exists(f"{doc_doc.checksum}.html"):
            raise Exception("Unable to regenerate pdf because the html file was never scraped!")

        direct_download = True
        # TODO: Once regenerate_from_scrape implemented and have download context,
        # use logic below to determine direct_download:
        # if download.direct_scrape or download.playwright_download:
        if direct_download:
            download_link = self.regenerate_from_html(doc_checksum=doc_doc.checksum)
        else:
            download_link = self.regenerate_from_scrape(doc_checksum=doc_doc.checksum)
        return download_link

    def regenerate_from_html(self, doc_checksum: str):
        # Download the html file to temp file, parse to pdf, and upload to s3.
        html = self.doc_client.read_utf8_object(f"{doc_checksum}.html")
        story = fitz.Story(html=html)
        page_bounds = fitz.paper_rect("letter")
        content_bounds = page_bounds + (36, 54, -36, -54)  # borders of 0.5 and .75 inches
        # add to use page.pdf instead of fitz so css is loaded.
        # async with self.playwright_context(url, cookies) as (base_page, context):
        with tempfile.NamedTemporaryFile() as pdf_temp:
            writer = fitz.DocumentWriter(pdf_temp)
            more_pages = 1
            while more_pages:
                current_page = writer.begin_page(page_bounds)
                more_pages, _ = story.place(content_bounds)
                story.draw(current_page)
                writer.end_page()
            writer.close()

            pdf_doc = fitz.Document(pdf_temp)
            pdf_bytes: bytes = pdf_doc.tobytes()  # type: ignore
            # pdf.Parser to update dates.
            self.doc_client.write_object_mem(
                relative_key=f"{doc_checksum}.html.pdf", object=pdf_bytes
            )

        # Pass signed url so doc re-renders with new pdf.
        url = self.doc_client.get_signed_url(f"{doc_checksum}.html.pdf", expires_in_seconds=60 * 60)
        return url

    def regenerate_from_scrape(self, doc_checksum: str):

        # TODO: How to generate DownloadContext without scraping whole site?
        # See run_scrape to get how download is generated.
        # async with self.playwright_context(url, download.request.cookies) as (
        #     page,
        #     _context,
        # ):
        #     await page.goto(url, wait_until="domcontentloaded")
        #     pdf_bytes = await page.pdf(display_header_footer=False, print_background=True)
        #     self.doc_client.write_object_mem(relative_key=dest_path, object=pdf_bytes)
        #     with tempfile.NamedTemporaryFile() as pdf_temp:
        #         pdf_temp.write(pdf_bytes)
        #         yield pdf_temp.name
        pass

    async def get_progress(self) -> float:
        return 0.0
