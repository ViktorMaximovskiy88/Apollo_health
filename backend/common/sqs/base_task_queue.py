import traceback

from backend.common.models.tasks import GenericTaskType
from backend.common.sqs.core import SQSClient, SQSListener


class BaseTaskQueue(SQSListener, SQSClient):
    def __init__(self, class_id: GenericTaskType, **kwargs) -> None:
        super().__init__(**kwargs)
        self._task_class = class_id

    async def enqueue(self, payload: dict) -> tuple[dict, GenericTaskType]:
        dedupe_key = self._task_class.get_dedupe_key(payload)
        task = await self._task_class.get_incomplete(dedupe_key)

        if not task:
            task = await self._task_class.create_pending(**payload, dedupe_key=dedupe_key)

        response = self.send(task.dict(), dedupe_key)
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

    async def handle_exception(self, ex: Exception, message: dict, body: dict):
        task = await self._get_task(body)
        if task:
            task = await task.update_failed(error=traceback.format_exc())
