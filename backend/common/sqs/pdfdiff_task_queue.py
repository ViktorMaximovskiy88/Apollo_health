import asyncio

from backend.common.models.doc_document import DocDocument
from backend.common.models.tasks import PDFDiffTask
from backend.common.services.text_compare.doc_text_compare import DocTextCompare
from backend.common.sqs.base_task_queue import BaseTaskQueue
from backend.common.storage.client import DocumentStorageClient


class PDFDiffTaskQueue(BaseTaskQueue):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs, class_id=PDFDiffTask)

    async def process_message(self, message: dict, body: dict):
        task = await self._get_task(body)
        task = await task.update_progress()

        try:
            self.logger.info(f"{self._task_class} processing started")
            doc_client = DocumentStorageClient()
            dtc = DocTextCompare(doc_client)

            (current_doc, prev_doc) = await asyncio.gather(
                DocDocument.find_one({"checksum": body["current_checksum"]}),
                DocDocument.find_one({"checksum": body["previous_checksum"]}),
            )
            dtc.compare(doc=current_doc, prev_doc=prev_doc)

            task = await task.update_finished()
            self.logger.info(f"{self._task_class} processing finished")

        except Exception as ex:
            self.logger.error(f"{self._task_class} error:", exc_info=True)
            await self.handle_exception(ex, message, body)
