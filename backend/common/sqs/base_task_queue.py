import traceback

from backend.common.models.tasks import GenericTaskType, TaskLog
from backend.common.sqs.core import SQSClient, SQSListener


class BaseTaskQueue(SQSListener, SQSClient):
    def __init__(self, class_id: GenericTaskType, **kwargs) -> None:
        super().__init__(**kwargs)
        self._task_class = class_id

    async def enqueue(self, payload: dict) -> tuple[dict, GenericTaskType]:
        group_id = self._task_class.get_group_id(payload)
        task = await self._task_class.get_incomplete(group_id)

        if not task:
            task = await self._task_class.create_pending(**payload, group_id=group_id)

        response = self.send(task.dict(), group_id)
        task = await task.update_queued(response)

        return response, task

    async def _get_task(self, body: dict):
        id = body.get("id", None)
        if not id:
            raise Exception("Missing message id")

        task = await self._task_class.get(body["id"])
        if not task:
            raise Exception(f"TaskLog not found id={body['id']}")

        return task

    async def begin_process_message(self, body: dict):
        task = await self._get_task(body)
        if task.is_complete:
            self.logger.info(f"{self._task_class} is already complete")
            return

        task = await task.update_progress()
        self.logger.info(f"{self._task_class} processing started")
        return task

    async def end_process_message(self, task: TaskLog):
        task = await task.update_finished()
        self.logger.info(f"{self._task_class} processing finished")

    async def handle_exception(self, ex: Exception, message: dict, body: dict):
        self.logger.error(f"{self._task_class} error:", exc_info=True)
        task = await self._get_task(body)
        if task:
            task = await task.update_failed(error=traceback.format_exc())
