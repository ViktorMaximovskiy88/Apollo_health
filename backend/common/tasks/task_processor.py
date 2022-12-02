import asyncio
import logging
from abc import ABC

from backend.common.models.doc_document import DocDocument
from backend.common.models.tasks import GenericTaskType, LineageTask, PDFDiffTask, TaskLog
from backend.common.services.lineage.core import LineageService
from backend.common.services.text_compare.doc_text_compare import DocTextCompare
from backend.common.storage.client import DocumentStorageClient


def task_processor_factory(task: TaskLog):
    task_type = type(task.payload).__name__
    if task_type == "PDFDiffTask":
        Processor = PDFDiffTaskProcessor
    elif task_type == "LineageTask":
        Processor = LineageTaskProcessor
    return Processor(logger=logging)


class TaskProcessor(ABC):
    def __init__(self, logger=logging) -> None:
        self.logger = logger

    async def exec(self, task_payload: GenericTaskType):
        raise NotImplementedError("exec is required")

    async def get_progress(self):
        raise NotImplementedError("get_progress is required")


class LineageTaskProcessor(TaskProcessor):
    def __init__(self, logger=logging) -> None:
        self.logger = logger
        self.lineage_service = LineageService(logger=logger)

    async def exec(self, task: LineageTask) -> None:
        if task.reprocess:
            await self.lineage_service.reprocess_lineage_for_site(task.site_id)
        else:
            await self.lineage_service.process_lineage_for_site(task.site_id)

    async def get_progress(self) -> float:
        return 0.0


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

    async def get_progress(self) -> float:
        return 0.0
