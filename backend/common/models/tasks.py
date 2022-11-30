from datetime import datetime, timedelta, timezone
from typing import TypeVar

from beanie import Indexed, Insert, PydanticObjectId, before_event

from backend.common.core.enums import TaskStatus
from backend.common.models.base_document import BaseDocument, BaseModel

GenericTaskType = TypeVar("GenericTaskType", "LineageTask", "PDFDiffTask")


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
    async def create_pending(cls, payload: GenericTaskType, **kwargs):
        task_type = type(payload).__name__
        task = cls(payload=payload, status=TaskStatus.PENDING, task_type=task_type, **kwargs)
        now = datetime.now(tz=timezone.utc)
        task.status_at = now
        task.log.append(
            TaskLogEntry(
                status=task.status,
                status_at=now,
            )
        )
        task = await task.save()
        return task

    @classmethod
    async def get_incomplete(cls: GenericTaskType, group_id: str) -> GenericTaskType | None:
        return await cls.find_one({"group_id": group_id, "is_complete": False})

    @classmethod
    async def get_incomplete_for_user(
        cls: GenericTaskType, user_id: PydanticObjectId
    ) -> GenericTaskType | None:
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
            and self.status_at.replace(tzinfo=None)
            < datetime.now(tz=timezone.utc) - timedelta(seconds=seconds)
        )

    def should_process(self, message_id: str, seconds: int) -> bool:
        return (
            self.is_queued() or self.has_failed() or self.is_stale(seconds)
        ) and self.message_id == message_id

    def has_been_queued(self) -> bool:
        queued = [log for log in self.log if log.status == TaskStatus.QUEUED]
        # TODO think on the message id part...
        return len(queued) > 0 and self.message_id

    async def update_queued(self, message_id: str) -> GenericTaskType:
        return await self._update_status(TaskStatus.QUEUED, message_id=message_id)

    async def update_progress(self) -> GenericTaskType:
        return await self._update_status(TaskStatus.IN_PROGRESS, is_complete=False)

    async def keep_alive(self) -> GenericTaskType:
        self.status_at = datetime.now(tz=timezone.utc)
        return await self.save()

    async def update_finished(self) -> GenericTaskType:
        return await self._update_status(TaskStatus.FINISHED, is_complete=True)

    async def update_failed(self, error: str) -> GenericTaskType:
        return await self._update_status(TaskStatus.FAILED, is_complete=True, error=error)

    async def _update_status(
        self,
        task_status: TaskStatus,
        message_id: str = None,
        is_complete=False,
        error: str | None = None,
    ) -> GenericTaskType:
        now = datetime.now(tz=timezone.utc)
        self.status = task_status
        self.is_complete = is_complete
        self.status_at = now

        if is_complete:
            self.completed_at = now

        if error:
            self.error = error

        if message_id:
            self.message_id = message_id

        self.log.append(
            TaskLogEntry(
                status=self.status,
                status_at=now,
            )
        )

        return await self.save()

    @before_event(Insert)
    def before_insert(self):
        self.created_at = datetime.now(tz=timezone.utc)
