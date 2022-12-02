from datetime import datetime, timedelta, timezone
from typing import TypeVar

from beanie import Indexed, Insert, PydanticObjectId, before_event
from pymongo import ReturnDocument

from backend.common.core.enums import TaskStatus
from backend.common.models.base_document import BaseDocument, BaseModel

GenericTaskType = TypeVar("GenericTaskType", "LineageTask", "PDFDiffTask")
T = TypeVar("T", bound="TaskLog")


class PDFDiffTask(BaseModel):
    current_checksum: str
    previous_checksum: str


class LineageTask(BaseModel):
    site_id: PydanticObjectId
    reprocess: bool = False


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

    def is_finished(self) -> bool:
        return self.is_complete and self.status == TaskStatus.FINISHED

    def has_failed(self) -> bool:
        return self.is_complete and self.status == TaskStatus.FAILED

    def is_queued(self) -> bool:
        return not self.is_complete and self.status == TaskStatus.QUEUED

    def is_stale(self, seconds: int) -> bool:
        return (
            not self.is_complete
            and self.status == TaskStatus.IN_PROGRESS
            and self.status_at
            < datetime.now(tz=timezone.utc).replace(tzinfo=None) - timedelta(seconds=seconds)
        )

    def should_process(self, message_id: str, seconds: int) -> bool:
        return (
            self.is_queued() or self.has_failed() or self.is_stale(seconds)
        ) and self.message_id == message_id

    def can_be_queued(self) -> bool:
        queued = [log for log in self.log if log.status == TaskStatus.QUEUED]
        return len(queued) == 0 and not self.message_id

    async def update_queued(self, message_id: str) -> T:
        return await self._update_status(TaskStatus.QUEUED, message_id=message_id)

    async def update_progress(self) -> T:
        return await self._update_status(TaskStatus.IN_PROGRESS, is_complete=False)

    async def keep_alive(self) -> T:
        self.status_at = datetime.now(tz=timezone.utc)
        return await self.save()

    async def update_finished(self) -> T:
        return await self._update_status(TaskStatus.FINISHED, is_complete=True)

    async def update_failed(self, error: str) -> T:
        return await self._update_status(TaskStatus.FAILED, is_complete=True, error=error)

    async def _update_status(
        self,
        task_status: TaskStatus,
        message_id: str = None,
        is_complete=False,
        error: str | None = None,
    ) -> T:
        now = datetime.now(tz=timezone.utc)

        payload = {
            "status": task_status,
            "is_complete": is_complete,
            "status_at": now,
        }

        if is_complete:
            payload["completed_at"] = now

        if error:
            payload["error"] = error

        if message_id:
            payload["message_id"] = message_id

        log_entry = TaskLogEntry(
            status=payload["status"],
            status_at=payload["status_at"],
        )

        updated = await self.get_motor_collection().find_one_and_update(
            {"_id": self.id},
            {"$set": payload, "$push": {"log": log_entry.dict()}},
            return_document=ReturnDocument.AFTER,
        )

        return TaskLog(**updated)

    @before_event(Insert)
    def before_insert(self):
        self.created_at = datetime.now(tz=timezone.utc)
