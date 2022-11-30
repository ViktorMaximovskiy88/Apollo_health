import asyncio
import logging
from abc import ABC

from backend.common.models.doc_document import DocDocument
from backend.common.models.tasks import GenericTaskType, LineageTask, PDFDiffTask
from backend.common.services.lineage.core import LineageService
from backend.common.services.text_compare.doc_text_compare import DocTextCompare
from backend.common.storage.client import DocumentStorageClient


def get_task_processor(task_payload: GenericTaskType):
    task_type = type(task_payload).__name__
    if task_type == "PDFDiffTask":
        return PDFDiffTaskProcessor
    elif task_type == "LineageTask":
        return LineageTaskProcessor


class TaskProcessor(ABC):
    def __init__(self, logger=logging) -> None:
        self.logger = logger

    async def exec(self, task: GenericTaskType):
        raise NotImplementedError(f"exec is required for {type(task).__name__}")


class LineageTaskProcessor(TaskProcessor):
    def __init__(self, logger=logging) -> None:
        self.logger = logger
        self.lineage_service = LineageService(logger=logger)

    async def exec(self, task: LineageTask):
        if task.reprocess:
            await self.lineage_service.reprocess_lineage_for_site(task.site_id)
        else:
            await self.lineage_service.process_lineage_for_site(task.site_id)


class PDFDiffTaskProcessor(TaskProcessor):
    def __init__(self, logger=logging) -> None:
        self.logger = logger

    async def exec(self, task: PDFDiffTask):
        doc_client = DocumentStorageClient()
        dtc = DocTextCompare(doc_client)

        (current_doc, prev_doc) = await asyncio.gather(
            DocDocument.find_one({"checksum": task.current_checksum}),
            DocDocument.find_one({"checksum": task.previous_checksum}),
        )
        dtc.compare(doc=current_doc, prev_doc=prev_doc)
