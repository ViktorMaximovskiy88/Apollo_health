import asyncio
import traceback
from collections.abc import Coroutine

from backend.common.models.tasks import GenericTaskType, PydanticObjectId, TaskLog
from backend.common.storage.client import DocumentStorageClient, TextStorageClient
from backend.common.tasks.processors import task_processor_factory
from backend.common.tasks.processors.doc_pipeline import DocPipelineTaskProcessor
from backend.common.tasks.processors.lineage import LineageTaskProcessor
from backend.common.tasks.processors.site_docs_pipeline import SiteDocsPipelineTaskProcessor
from backend.common.tasks.sqs import SQSBase
from backend.common.tasks.task_processor import TaskProcessor

# TODO shouldnt be here...
from backend.scrapeworker.document_tagging.taggers import Taggers, indication_tagger, therapy_tagger

# poor man's DI (to avoid _relatively_ costly operations from repeating)
# TODO a 'caching; doc/text client since we know we are operating per
# doc within our doc tasks
taggers = Taggers(indication=indication_tagger, therapy=therapy_tagger)
dependency_map = {
    "indication_tagger": taggers.indication,
    "therapy_tagger": taggers.therapy,
    "text_client": TextStorageClient(),
    "doc_client": DocumentStorageClient(),
}


class TaskQueue(SQSBase):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.keep_alive_task: asyncio.Task = None
        self.current_message = None
        self.current_task = None
        self.listening = False
        self.keep_alive_seconds = 5
        self.visibility_timeout = self.keep_alive_seconds * 2
        self.cancel_timeout = self.visibility_timeout * 2

    async def onshutdown(self):
        self.logger.info("Shutting down")
        self.listening = False
        await asyncio.sleep(5)

        if self.current_message:
            self.logger.info(
                f"message_id={self.current_message.message_id} visibility={self.visibility_timeout}"
            )
            self.current_message.change_visibility(VisibilityTimeout=self.visibility_timeout)

        if self.current_task:
            self.logger.info(f"task_id={self.current_task.id} has been interupted")
            await self.current_task.update_canceled()

    async def enqueue(
        self, payload: GenericTaskType, created_by: PydanticObjectId | None = None
    ) -> TaskLog:
        task: TaskLog = await TaskLog.upsert(payload=payload, created_by=created_by)

        if task.can_be_queued():
            self.logger.info(f"queueing new message group_id={task.group_id}")
            response = self.send(task.dict(), task.group_id)
            task = await task.update_queued(message_id=response["MessageId"])

        return task

    async def keep_alive(self, seconds: int, message, task: TaskLog, on_progress: Coroutine):
        while True:
            print("before is this working as expected")
            await task.keep_alive()
            message.change_visibility(VisibilityTimeout=self.visibility_timeout)
            await on_progress()
            await asyncio.sleep(self.keep_alive_seconds)
            print("afteris this working as expected")

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

                    # something bad happened
                    if task.is_stale(self.cancel_timeout):
                        await task.update_canceled()
                        message.delete()
                        self.logger.info(
                            f"message_id={message.message_id} is stale and now canceled"
                        )
                        continue

                    if task.is_hidden(message.message_id):
                        self.logger.info(f"message_id={message.message_id} is hidden")
                        continue

                    try:
                        task = await task.update_progress()
                        self.logger.info(f"{task.task_type} processing started")

                        # DocTask Processor
                        task_processor: TaskProcessor = task_processor_factory(task)

                        # TODO need refactor due to circular dep, cheating now
                        # this composite tasks are another breed; refactor incoming
                        if task.task_type == "DocPipelineTask":
                            task_processor = DocPipelineTaskProcessor()
                        elif task.task_type == "SiteDocsPipelineTask":
                            task_processor = SiteDocsPipelineTaskProcessor()
                        elif task.task_type == "LineageTask":
                            task_processor = LineageTaskProcessor()

                        if not task_processor:
                            raise Exception("no task processor found")

                        self.keep_alive_task = asyncio.create_task(
                            self.keep_alive(
                                self.keep_alive_seconds, message, task, task_processor.get_progress
                            )
                        )
                        result = await task_processor.exec(task.payload)
                        self.keep_alive_task.cancel()

                        task = await task.update_finished(result)
                        self.logger.info(f"{task.task_type} processing finished")
                        message.delete()
                    except asyncio.CancelledError:
                        # cancelling the keep alive
                        pass
                    except Exception:
                        self.logger.error("task error:", exc_info=True)
                        await task.update_failed(error=traceback.format_exc())

                except Exception:
                    self.logger.error("queue error:", exc_info=True)

                self.current_message = None
                self.current_task = None

    async def _get_task_by_message(self, message):
        task = await TaskLog.find_by_message_id(message.message_id)
        if not task:
            message.change_visibility(VisibilityTimeout=self.keep_alive_seconds)
            raise Exception(f"TaskLog not found message_id={message.message_id} {message.body}")
        return task
