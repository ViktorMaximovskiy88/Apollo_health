# import io
import logging
import tempfile

# import aiofiles
# import boto3
import fitz

import backend.common.models.tasks as tasks

# from backend.app.core.settings import Settings
from backend.common.models.doc_document import DocDocument
from backend.common.models.document import RetrievedDocument
from backend.common.models.pipeline import PipelineRegistry

# from backend.common.models.shared import DocDocumentLocation
from backend.common.storage.client import DocumentStorageClient, TextStorageClient
from backend.common.tasks.task_processor import TaskProcessor

# from backend.scrapeworker.common.models import DownloadContext, Request
# from backend.scrapeworker.file_parsers import pdf


class RescrapeDocProcessor(TaskProcessor):

    dependencies: list[str] = [
        "doc_client",
        "text_client",
    ]

    def __init__(
        self,
        doc_client: DocumentStorageClient | None = None,
        text_client: TextStorageClient | None = None,
        logger=logging,
    ) -> None:
        self.logger = logger
        self.doc_client = doc_client or DocumentStorageClient()
        self.text_client = text_client or TextStorageClient()

    async def exec(self, task: tasks.ContentTask):
        stage_versions = await PipelineRegistry.fetch()
        # TODO: doc_doc_id is retr_doc_id passed from pdf viewer 401 button,
        # but doc_doc_id not being set or retr_doc_id not being passed in type error.
        retr_doc: RetrievedDocument | None = await RetrievedDocument.find_one(
            {"_id": task.doc_doc_id},
        )
        if not retr_doc:
            raise Exception(f"retr_doc {task.doc_doc_id} not found")

        doc_doc: DocDocument | None = await DocDocument.find_one(
            {"retrieved_document_id": retr_doc.id},
        )
        if not doc_doc:
            raise Exception(f"cannot find doc_doc with retr_doc {retr_doc.id}")

        if (
            doc_doc.get_stage_version("content") == stage_versions.content.version
            and not task.reprocess
        ):
            return

        # Make sure doc has existing html doc already scraped.
        # If the html doc does not exist, you will need to refactor the
        # scraper to support rescraping 1 doc vs the entire site.
        doc_checksum = f"{doc_doc.checksum}"
        doc_client: DocumentStorageClient = DocumentStorageClient()
        if not doc_client.object_exists(f"{doc_checksum}.html"):
            raise Exception("Unable to regenerate pdf!")

        # Download the html file to temp file, parse to pdf, and upload to s3.
        with doc_client.read_object_to_tempfile(f"{doc_checksum}.html") as html_file:
            # download: DownloadContext = DownloadContext(
            #     request=Request(url=temp_pdf_path), file_extension=doc_doc.file_extension
            # )
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

                pdf_doc = fitz.Document(pdf_temp)
                pdf_bytes: bytes = pdf_doc.tobytes()  # type: ignore
                self.doc_client.write_object_mem(
                    relative_key=f"{doc_checksum}.pdf", object=pdf_bytes
                )

                # TODO: call this after to parse and update dates.
                # location: DocDocumentLocation = doc_doc.locations[0]
                # await pdf.PdfParse(
                #     pdf_temp.name,
                #     url,
                #     link_text=location.link_text,
                #     scrape_method_config=scrape_method_config,
                #     download=download,
                # ).update_parsed_content(parsed_content)
