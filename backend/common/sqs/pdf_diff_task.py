import traceback

from backend.common.models.task_log import PDFDiffTask, TaskStatus
from backend.common.sqs.core import SQSClient, SQSListener


# TODO possibly move some crud-y tasks
# still formulating needs before we refactor
class PDFDiffTaskQueue(SQSListener, SQSClient):
    async def enqueue(self, key: str):
        task = PDFDiffTask(key=key, status=TaskStatus.PENDING)
        task = await task.save()
        response = self.send(task.dict(), dedupe_id=str(task.id))
        print(response)
        # success or fail
        task.status = TaskStatus.QUEUED
        task = await task.save()

    async def process_message(self, body: dict, message: dict):
        task = await PDFDiffTask.get(body["id"])
        task.status = TaskStatus.IN_PROGRESS
        task = await task.save()

        print("PROCESS AND DO THINGS")

        task = await PDFDiffTask.get(body["id"])
        task.status = TaskStatus.FINISHED
        task = await task.save()

    async def handle_exception(self, ex: Exception, message: dict, body: dict):
        task = await PDFDiffTask.get(body["id"])
        task.status = TaskStatus.FAILED
        task.error = traceback.format_exc()
        task = await task.save()
        self.logger.error(f"task_id={body['id']}")
