import logging
import traceback

from backend.common.models.task_log import LineageTask, TaskLog, TaskStatus
from backend.common.services.lineage.core import LineageService
from backend.common.sqs.core import SQSClient, SQSListener


class LineageTaskQueue(SQSListener, SQSClient):
    def __init__(
        self, queue_url: str, logger=logging, max_number_of_messages=1, wait_time_seconds=1
    ) -> None:
        super().__init__(queue_url, logger, max_number_of_messages, wait_time_seconds)
        self.lineage_service = LineageService(logger=logger)

    async def enqueue(self, payload: dict) -> tuple[dict, TaskLog]:
        dedupe_key = f"LineageTask-{payload['site_id']}"

        task = await LineageTask.find_one(
            {
                "site_id": payload["site_id"],
                "is_complete": False,
            }
        )

        if not task:
            task = LineageTask(
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

        return response, task

    async def process_message(self, message: dict, body: dict):
        id = body.get("id", None)
        if not id:
            raise Exception("Missing message id")

        task = await LineageTask.get(body["id"])
        if not task:
            raise Exception(f"TaskLog not found id={body['id']}")

        task.status = TaskStatus.IN_PROGRESS
        task = await task.save()

        try:
            self.logger.info("LineageTask processing started")

            if task.reprocess:
                await self.lineage_service.reprocess_lineage_for_site(task.site_id)
            else:
                await self.lineage_service.process_lineage_for_site(task.site_id)

            task.is_complete = True
            task.status = TaskStatus.FINISHED
            task = await task.save()
            self.logger.info("LineageTask processing finished")

        except Exception as ex:
            self.logger.error("LineageTask error:", exc_info=True)
            await self.handle_exception(ex, message, body)

    async def handle_exception(self, ex: Exception, message: dict, body: dict):
        id = body.get("id", None)
        if not id:
            raise Exception("Missing message id")

        task = await LineageTask.get(body["id"])
        if task:
            task.status = TaskStatus.FAILED
            task.is_complete = True
            task.error = traceback.format_exc()
            task = await task.save()
