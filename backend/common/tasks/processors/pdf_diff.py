import asyncio
import logging

import backend.common.models.tasks as tasks
from backend.common.models.doc_document import DocDocument
from backend.common.services.text_compare.doc_text_compare import DocTextCompare
from backend.common.storage.client import DocumentStorageClient
from backend.common.tasks.task_processor import TaskProcessor


class PDFDiffTaskProcessor(TaskProcessor):

    dependencies: list[str] = []

    def __init__(self, logger=logging) -> None:
        self.logger = logger

    async def exec(self, task: tasks.PDFDiffTask):
        doc_client = DocumentStorageClient()
        dtc = DocTextCompare(doc_client)

        (current_doc, prev_doc) = await asyncio.gather(
            DocDocument.find_one({"checksum": task.current_checksum}),
            DocDocument.find_one({"checksum": task.previous_checksum}),
        )
        dtc.compare(doc=current_doc, prev_doc=prev_doc)

        return {
            "new_key": f"{task.current_checksum}-{task.previous_checksum}-new.pdf",
            "prev_key": f"{task.current_checksum}-{task.previous_checksum}-prev.pdf",
        }

    async def get_progress(self) -> float:
        return 0.0
