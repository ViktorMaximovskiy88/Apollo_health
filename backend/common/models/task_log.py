from datetime import datetime, timezone

from beanie import Indexed, Insert, PydanticObjectId, Replace, UnionDoc, before_event

from backend.common.core.enums import TaskStatus
from backend.common.models.base_document import BaseDocument, BaseModel
from backend.common.models.task_types import GenericTaskType


class TaskLog(UnionDoc):
    class Settings:
        name = "TaskLog"
        use_revision = False


class TaskLogEntry(BaseModel):
    response: dict | None
    status: TaskStatus
    created_at: datetime


class BaseTask(BaseDocument):
    created_at: datetime | None = None
    updated_at: datetime | None = None

    created_by: PydanticObjectId | None

    status: TaskStatus = TaskStatus.PENDING
    status_at: datetime | None = None

    error: str | None = None
    is_complete: bool = False
    dedupe_key: Indexed(str)

    log: list[TaskLogEntry] = []

    @classmethod
    async def create_pending(cls: GenericTaskType, **payload) -> GenericTaskType:
        task: GenericTaskType = cls(
            **payload,
            status=TaskStatus.PENDING,
        )
        task.log.append(
            TaskLogEntry(
                status=task.status,
                created_at=datetime.now(tz=timezone.utc),
            )
        )
        return await task.save()

    @classmethod
    async def get_incomplete(cls: GenericTaskType, dedupe_key: str) -> GenericTaskType | None:
        return await cls.find_one({"dedupe_key": dedupe_key, "is_complete": False})

    async def update_queued(self, response: dict) -> GenericTaskType:
        return await self._update_status(TaskStatus.QUEUED, response=response)

    async def update_progress(self) -> GenericTaskType:
        return await self._update_status(TaskStatus.IN_PROGRESS)

    async def update_finished(self) -> GenericTaskType:
        return await self._update_status(TaskStatus.FINISHED, is_complete=True)

    async def update_failed(self, error: str) -> GenericTaskType:
        return await self._update_status(TaskStatus.FAILED, is_complete=True, error=error)

    async def _update_status(
        self,
        task_status: TaskStatus,
        response: dict = None,
        is_complete=False,
        error: str | None = None,
    ) -> GenericTaskType:
        self.status = task_status
        self.is_complete = is_complete
        if error:
            self.error = error
        self.log.append(
            TaskLogEntry(
                response=response,
                status=self.status,
                created_at=datetime.now(tz=timezone.utc),
            )
        )
        return await self.save()

    @before_event(Insert)
    def before_insert(self):
        now = datetime.now(tz=timezone.utc)
        self.created_at = now
        self.updated_at = now
        self.status_at = now

    @before_event(Replace)
    def before_replace(self):
        self.updated_at = datetime.now(tz=timezone.utc)
