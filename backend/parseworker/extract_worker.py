import pdfplumber
import redis
from contextlib import asynccontextmanager
from datetime import datetime
from beanie.odm.operators.update.general import Inc
from backend.common.models.content_extraction_task import (
    ContentExtractionResult,
    ContentExtractionTask,
)
from backend.common.models.document import RetrievedDocument
from backend.common.models.site import Site
from backend.common.models.user import User
from backend.common.core.config import config

from backend.app.utils.logger import Logger, create_and_log, update_and_log_diff
from backend.common.storage.client import DocumentStorageClient


class ExtractWorker:
    def __init__(
        self,
        extract_task: ContentExtractionTask,
        retrieved_document: RetrievedDocument,
        site: Site,
    ) -> None:
        self.extract_task = extract_task
        self.site = site
        self.doc_client = DocumentStorageClient()
        self.retrieved_document = retrieved_document
        self.logger = Logger()
        self.redis = redis.from_url(
            config["REDIS_URL"], password=config["REDIS_PASSWORD"]
        )
        self.user = None

    async def get_user(self):
        if not self.user:
            self.user = await User.by_email("admin@mmitnetwork.com")
        if not self.user:
            raise Exception("No user found")
        return self.user

    async def process_table(self, page, table: list[list[str | None]]):
        header = table[0]
        for row_number, line in enumerate(table[1:]):
            row = {}
            for i, field in enumerate(header):
                row[field] = line[i]
            await self.extract_task.update(
                Inc({ContentExtractionTask.extraction_count: 1})
            )
            result = ContentExtractionResult(
                page=page.page_number,
                row=row_number,
                site_id=self.extract_task.site_id,
                scrape_task_id=self.extract_task.scrape_task_id,
                retrieved_document_id=self.extract_task.retrieved_document_id,
                content_extraction_task_id=self.extract_task.id,
                collection_time=datetime.now(),
                result=row,
            )
            await result.save()

    def skip_table(self, table: list[list[str]]):
        return table[0][0] == "$"

    async def process_page(self, page):
        tables = page.extract_tables()
        for table in tables:
            if self.skip_table(table):
                continue
            await self.process_table(page, table)

    async def process_file(self, file_path: str):
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                await self.process_page(page)

    async def run_extraction(self):
        filename = f"{self.retrieved_document.checksum}.pdf"
        with self.doc_client.read_document_to_tempfile(filename) as file_path:
            await self.process_file(file_path)
