from datetime import datetime, timedelta, timezone
from typing import Any, TypeVar

from beanie import Indexed, PydanticObjectId
from pymongo import ReturnDocument

from backend.common.core.enums import TaskStatus
from backend.common.models.base_document import BaseDocument, BaseModel

GenericTaskType = TypeVar(
    "GenericTaskType",
    "PDFDiffTask",
    "ContentTask",
    "DateTask",
    "DocTypeTask",
    "TagTask",
    "DocPipelineTask",
    "SiteDocsPipelineTask",
    "LineageTask",
)
T = TypeVar("T", bound="TaskLog")


class DocTask(BaseModel):
    doc_doc_id: PydanticObjectId
    reprocess: bool = False


class DocPipelineTask(DocTask):
    pass


class ContentTask(DocTask):
    pass


class DateTask(DocTask):
    pass


class DocTypeTask(DocTask):
    pass


class TagTask(DocTask):
    pass


class SiteTask(BaseModel):
    site_id: PydanticObjectId
    reprocess: bool = False


class SiteDocsPipelineTask(SiteTask):
    pass


class LineageTask(SiteTask):
    pass


class PDFDiffTask(BaseModel):
    current_checksum: str
    previous_checksum: str


def get_group_id(payload: GenericTaskType):
    values = [str(value) for value in payload.dict().values()]
    group_id = "-".join(values)
    return f"{type(payload).__name__}-{group_id}"


class TaskLogEntry(BaseModel):
    status: TaskStatus
    status_at: datetime


class TaskLog(BaseDocument):
    created_at: datetime | None = None
    created_by: PydanticObjectId | None

    status: TaskStatus = TaskStatus.PENDING
    status_at: datetime | None = None

    completed_at: datetime | None = None
    is_complete: bool = False

    error: str | None = None
    group_id: Indexed(str)
    message_id: Indexed(str) | None

    log: list[TaskLogEntry] = []

    task_type: Indexed(str)
    payload: GenericTaskType
    result: Any | None = None

    def get_group_id(self):
        return get_group_id(self.payload)

    @classmethod
    async def find_by_message_id(cls, message_id: str):
        return await cls.find_one({"message_id": message_id})

    @classmethod
    async def upsert(cls, payload: GenericTaskType, created_by: PydanticObjectId | None):
        task_type = type(payload).__name__
        now = datetime.now(tz=timezone.utc)
        group_id = get_group_id(payload)
        status = TaskStatus.PENDING

        task = cls(
            group_id=group_id,
            payload=payload,
            status=status,
            task_type=task_type,
            status_at=now,
            created_by=created_by,
            created_at=now,
            log=[
                TaskLogEntry(
                    status=status,
                    status_at=now,
                )
            ],
        )

        saved_task = await cls.get_motor_collection().find_one_and_update(
            {
                "group_id": group_id,
                "is_complete": False,
            },
            {"$setOnInsert": task.dict()},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
        return TaskLog(**saved_task)

    @classmethod
    async def get_incomplete_for_user(cls: T, user_id: PydanticObjectId) -> T | None:
        return await cls.find_many({"created_by": user_id, "is_complete": False}).to_list()

    def is_progressing(self) -> bool:
        return not self.is_complete and self.status == TaskStatus.IN_PROGRESS

    def is_finished(self) -> bool:
        return self.is_complete and self.status == TaskStatus.FINISHED

    def has_failed(self) -> bool:
        return self.is_complete and self.status == TaskStatus.FAILED

    def is_queued(self) -> bool:
        return not self.is_complete and self.status == TaskStatus.QUEUED

    def is_canceled(self) -> bool:
        return self.is_complete and self.status == TaskStatus.CANCELED

    def is_stale(self, seconds: int) -> bool:
        return (
            not self.is_complete
            and self.status == TaskStatus.IN_PROGRESS
            and self.status_at
            < datetime.now(tz=timezone.utc).replace(tzinfo=None) - timedelta(seconds=seconds)
        )

    def is_hidden(self, message_id: str) -> bool:
        return (
            self.is_progressing() or self.has_failed() or self.is_canceled()
        ) and self.message_id == message_id

    def can_be_queued(self) -> bool:
        queued = [log for log in self.log if log.status == TaskStatus.QUEUED]
        return len(queued) == 0 and not self.message_id

    async def update_queued(self, message_id: str) -> T:
        return await self._update_status(TaskStatus.QUEUED, message_id=message_id)

    async def update_progress(self) -> T:
        return await self._update_status(TaskStatus.IN_PROGRESS, is_complete=False)

    async def keep_alive(self) -> T:
        return await self._update_status(task_status=self.status, append_log=False)

    async def update_finished(self, result: dict[str, any] | None) -> T:
        return await self._update_status(TaskStatus.FINISHED, is_complete=True, result=result)

    async def update_failed(self, error: str) -> T:
        return await self._update_status(TaskStatus.FAILED, is_complete=True, error=error)

    async def update_canceled(self) -> T:
        return await self._update_status(TaskStatus.CANCELED, is_complete=True)

    async def _update_status(
        self,
        task_status: TaskStatus,
        message_id: str = None,
        is_complete=False,
        result: dict[str, any] | None = None,
        error: str | None = None,
        append_log: bool = True,
    ) -> T:
        now = datetime.now(tz=timezone.utc)

        payload = {
            "status": task_status,
            "is_complete": is_complete,
            "status_at": now,
        }

        if result:
            payload["result"] = result

        if is_complete:
            payload["completed_at"] = now

        if error:
            payload["error"] = error

        if message_id:
            payload["message_id"] = message_id

        update_op = {"$set": payload}
        if append_log:
            log_entry = TaskLogEntry(
                status=payload["status"],
                status_at=payload["status_at"],
            )
            update_op["$push"] = {"log": log_entry.dict()}

        updated = await self.get_motor_collection().find_one_and_update(
            {"_id": self.id},
            update_op,
            return_document=ReturnDocument.AFTER,
        )

        return TaskLog(**updated)
