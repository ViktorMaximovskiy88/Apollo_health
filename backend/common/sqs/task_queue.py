import traceback

from backend.common.models.tasks import GenericTaskType, PydanticObjectId, TaskLog, get_group_id
from backend.common.sqs.core import SQSBase
from backend.common.sqs.task_processor import get_task_processor


class TaskQueue(SQSBase):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    async def enqueue(
        self, payload: GenericTaskType, created_by: PydanticObjectId | None = None
    ) -> TaskLog:
        group_id = get_group_id(payload)
        task: TaskLog = await TaskLog.get_incomplete(group_id)

        if not task:
            task = await TaskLog.create_pending(
                payload=payload,
                group_id=group_id,
                created_by=created_by,
            )

        response = self.send(task.dict(), group_id)
        message_id = response["MessageId"]
        if not task.message_id or task.message_id != message_id:
            task = await task.update_queued(message_id)

        return task

    async def listen(self):
        while True:
            for (message, payload) in self.receive():
                self.logger.info(f"received message_id={message.message_id}")
                try:
                    task: TaskLog = await self._get_task(payload)

                    if task.is_complete:
                        self.logger.info(f"{task.task_type} is already complete")
                        message.delete()
                        continue

                    task = await task.update_progress()
                    self.logger.info(f"{task.task_type} processing started")

                    try:
                        Processor = get_task_processor(task.payload)
                        await Processor(logger=self.logger).exec(task.payload)
                    except Exception:
                        self.logger.error("task error:", exc_info=True)
                        await task.update_failed(error=traceback.format_exc())
                        message.delete()
                        continue

                    task = await task.update_finished()
                    self.logger.info(f"{task.task_type} processing finished")
                    message.delete()

                except Exception:
                    self.logger.error("queue error:", exc_info=True)

    async def _get_task(self, body: dict):
        id = body.get("id", None)
        if not id:
            raise Exception("Missing message id")

        task = await TaskLog.get(body["id"])
        if not task:
            raise Exception(f"TaskLog not found id={body['id']}")

        return task
