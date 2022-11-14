import asyncio
import traceback

from backend.common.models.doc_document import DocDocument
from backend.common.models.task_log import PDFDiffTask, TaskStatus
from backend.common.services.text_compare.doc_text_compare import DocTextCompare
from backend.common.sqs.core import SQSClient, SQSListener
from backend.common.storage.client import DocumentStorageClient


# TODO move some crud-y tasks
# hide some task logic
# still formulating needs before we refactor
class PDFDiffTaskQueue(SQSListener, SQSClient):
    async def enqueue(self, payload: dict):
        dedupe_key = f"PDFDiffTask-{payload['current_checksum']}-{payload['previous_checksum']}"

        task = await PDFDiffTask.find_one(
            {
                "current_checksum": payload["current_checksum"],
                "previous_checksum": payload["previous_checksum"],
                "is_complete": False,
            }
        )

        if not task:
            task = PDFDiffTask(
                **payload,
                dedupe_key=dedupe_key,
                status=TaskStatus.PENDING,
            )
            task = await task.save()
            response = self.send(task.dict(), dedupe_key)
            task.status = TaskStatus.QUEUED
            task = await task.save()
        else:
            response = self.send(task.dict(), dedupe_key)

        return response

    async def process_message(self, message: dict, body: dict):
        id = body.get("id", None)
        if not id:
            raise Exception("Missing message id")

        task = await PDFDiffTask.get(body["id"])
        if not task:
            raise Exception(f"TaskLog not found id={body['id']}")

        task.status = TaskStatus.IN_PROGRESS
        task = await task.save()

        try:
            self.logger.info("PDFDiffTask processing started")
            doc_client = DocumentStorageClient()
            dtc = DocTextCompare(doc_client)

            (current_doc, prev_doc) = await asyncio.gather(
                DocDocument.find_one({"checksum": body["current_checksum"]}),
                DocDocument.find_one({"checksum": body["previous_checksum"]}),
            )
            dtc.compare(doc=current_doc, prev_doc=prev_doc)

            task.is_complete = True
            task.status = TaskStatus.FINISHED
            task = await task.save()
            self.logger.info("PDFDiffTask processing finished")

        except Exception as ex:
            self.logger.error("PDFDiffTask error:", exc_info=True)
            await self.handle_exception(ex, message, body)

    async def handle_exception(self, ex: Exception, message: dict, body: dict):
        id = body.get("id", None)
        if not id:
            raise Exception("Missing message id")

        task = await PDFDiffTask.get(body["id"])
        if task:
            task.status = TaskStatus.FAILED
            task.is_complete = True
            task.error = traceback.format_exc()
            task = await task.save()
