import sys
import traceback
from pathlib import Path

import newrelic.agent

newrelic.agent.initialize(Path(__file__).parent / "newrelic.ini")
sys.path.append(str(Path(__file__).parent.joinpath("../..").resolve()))

import asyncio
import logging

from backend.common.db.init import init_db
from backend.common.models.task_log import PDFDiffTask, TaskStatus
from backend.common.sqs.core import SQSClient, SQSListener

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pdf_diff_task")


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
        self.logger.error(f"task_id={body['id']}", exc_info=1)


async def main():
    await init_db()
    logger.info("Starting the pdf queue worker")

    queue = PDFDiffTaskQueue(
        queue_name="pdf-diff-queue.fifo",
        endpoint_url="http://localhost:9324",
        logger=logger,
    )

    await queue.enqueue("TIASDKJAHSKDJHAKSJDHJH")
    await queue.listen()


if __name__ == "__main__":
    asyncio.run(main())
