import asyncio
import signal
import traceback
from collections.abc import Coroutine

from backend.common.models.tasks import GenericTaskType, PydanticObjectId, TaskLog
from backend.common.tasks.sqs import SQSBase
from backend.common.tasks.task_processor import TaskProcessor, task_processor_factory


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
            self.current_message.change_visibility(VisibilityTimeout=self.keep_alive_seconds)

        loop = asyncio.get_event_loop()
        tasks = asyncio.gather(*asyncio.all_tasks(loop=loop), return_exceptions=True)
        tasks.add_done_callback(lambda t: loop.stop())
        tasks.cancel()

        # TODO some better handling here; lets catch the known exception?
        # TODO can that backfire (aka is it a valid exception in some cases)?
        while not tasks.done() and not loop.is_closed():
            loop.run_forever()

    async def enqueue(
        self, payload: GenericTaskType, created_by: PydanticObjectId | None = None
    ) -> TaskLog:

        task: TaskLog = await TaskLog.upsert(payload, created_by=created_by)

        if task.can_be_queued():
            response = self.send(task.dict(), task.group_id)
            task = await task.update_queued(message_id=response["MessageId"])

        return task

    async def keep_alive(self, seconds: int, message, task: TaskLog, on_progress: Coroutine):
        while True:
            message.change_visibility(VisibilityTimeout=seconds)
            await on_progress()
            await task.keep_alive()
            await asyncio.sleep(seconds)

    async def listen(self):
        self.listening = True
        self.logger.info("listening for messages")
        while self.listening:
            for (message, _payload) in self.receive():
                self.current_message = message
                self.logger.info(f"received message_id={message.message_id}")
                task: TaskLog = None
                try:
                    task = await self._get_task_by_message(message)
                    self.current_task = task

                    if not task.should_process(message.message_id, self.keep_alive_seconds):
                        self.logger.info(f"message_id={message.message_id} is already complete")
                        message.delete()
                        continue

                    task = await task.update_progress()
                    self.logger.info(f"{task.task_type} processing started")

                    try:
                        task_processor: TaskProcessor = task_processor_factory(logger=self.logger)
                        self.keep_alive_task = asyncio.create_task(
                            self.keep_alive(
                                self.keep_alive_seconds, message, task, task_processor.get_progress
                            )
                        )
                        await task_processor.exec()
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
                except Exception:
                    self.logger.error("queue error:", exc_info=True)

                self.current_message = None

    async def _get_task_by_message(self, message):
        task = await TaskLog.find_by_message_id(message.message_id)
        if not task:
            message.change_visibility(VisibilityTimeout=self.keep_alive_seconds)
            raise Exception(f"TaskLog not found message_id={message.message_id}")
        return task

    async def _get_task(self, body: dict):
        id = body.get("id", None)
        if not id:
            raise Exception("Missing message id")

        task = await TaskLog.get(body["id"])
        if not task:
            raise Exception(f"TaskLog not found id={body['id']}")

        return task
