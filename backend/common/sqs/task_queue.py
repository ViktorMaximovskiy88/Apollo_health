import asyncio
import signal
import traceback

from backend.common.models.tasks import GenericTaskType, PydanticObjectId, TaskLog, get_group_id
from backend.common.sqs.core import SQSBase
from backend.common.sqs.task_processor import get_task_processor


class TaskQueue(SQSBase):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.keep_alive_task: asyncio.Task = None
        self.current_message = None
        self.current_task = None
        self.listening = False
        self.keep_alive_seconds = 10
        signal.signal(signal.SIGTERM, lambda signum, frame: self.onshutdown(signum, frame))
        signal.signal(signal.SIGINT, lambda signum, frame: self.onshutdown(signum, frame))

    def onshutdown(self, signum, frame):
        self.logger.info(f"Received Signal {signum}")
        self.listening = False

        if self.current_message:
            self.logger.info(f"message_id={self.current_message.message_id} change_visibility to 0")
            self.current_message.change_visibility(VisibilityTimeout=10)

        loop = asyncio.get_event_loop()
        tasks = asyncio.gather(*asyncio.all_tasks(loop=loop), return_exceptions=False)
        tasks.cancel()
        tasks.add_done_callback(lambda t: loop.stop())
        while not tasks.done() and not loop.is_closed():
            loop.run_forever()

    async def enqueue(
        self, payload: GenericTaskType, created_by: PydanticObjectId | None = None
    ) -> TaskLog:
        group_id = get_group_id(payload)
        # lets make sure its all going to primary or just redis...
        # doesnt exist by group_id (wont have message_id yet) and incomplete
        task: TaskLog = await TaskLog.get_incomplete(group_id)

        if not task:
            task = await TaskLog.create_pending(
                payload=payload,
                group_id=group_id,
                created_by=created_by,
            )

        if not task.has_been_queued():
            response = self.send(task.dict(), group_id)
            message_id = response["MessageId"]
            task = await task.update_queued(message_id)

        return task

    async def keep_alive(self, message, task: TaskLog, seconds: int):
        while True:
            message.change_visibility(VisibilityTimeout=seconds)
            await task.keep_alive()
            await asyncio.sleep(seconds)

    async def listen(self):
        self.listening = True
        self.logger.info("listening for messages")
        while self.listening:
            for (message, _payload) in self.receive():
                self.current_message = message
                self.logger.info(f"received message_id={message.message_id}")
                task: TaskLog
                try:
                    task = await self._get_task_by_message_id(message.message_id)
                    self.current_task = task

                    if not task.should_process(message.message_id, self.keep_alive_seconds):
                        self.logger.info(f"message_id={message.message_id} is already complete")
                        message.delete()
                        continue

                    task = await task.update_progress()
                    self.logger.info(f"{task.task_type} processing started")

                    try:
                        Processor = get_task_processor(task.payload)
                        self.keep_alive_task = asyncio.create_task(
                            self.keep_alive(message, task, self.keep_alive_seconds)
                        )
                        await Processor(logger=self.logger).exec(task.payload)
                        self.keep_alive_task.cancel()

                        task = await task.update_finished()
                        self.logger.info(f"{task.task_type} processing finished")
                        message.delete()
                    except asyncio.CancelledError:
                        # cancelling the keep alive
                        pass
                    except Exception:
                        self.logger.error("task error:", exc_info=True)
                        await task.update_failed(error=traceback.format_exc())

                except asyncio.CancelledError:
                    self.logger.warn("canceling tasks")
                    if task:
                        await task.update_failed(error=traceback.format_exc())

                except Exception:
                    self.logger.error("queue error:", exc_info=True)
                    if task:
                        await task.update_failed(error=traceback.format_exc())

                self.current_message = None

    async def _get_task_by_message_id(self, message_id: str):
        task = await TaskLog.find_one({"message_id": message_id})
        if not task:
            raise Exception(f"TaskLog not found message_id={message_id}")

        return task

    async def _get_task(self, body: dict):
        id = body.get("id", None)
        if not id:
            raise Exception("Missing message id")

        task = await TaskLog.get(body["id"])
        if not task:
            raise Exception(f"TaskLog not found id={body['id']}")

        return task
