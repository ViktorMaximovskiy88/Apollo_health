from datetime import datetime, timezone

from beanie import Insert, PydanticObjectId, Replace, UnionDoc, before_event

from backend.common.core.enums import TaskStatus
from backend.common.models.base_document import BaseDocument


class TaskLog(UnionDoc):
    class Settings:
        name = "TaskLog"
        use_revision = False


class BaseTask(BaseDocument):
    created_at: datetime | None = None
    updated_at: datetime | None = None

    created_by: PydanticObjectId | None

    status: TaskStatus = TaskStatus.PENDING
    status_at: datetime | None = None

    error: str | None = None

    @before_event(Insert)
    def insert_dates(self):
        now = datetime.now(tz=timezone.utc)
        self.created_at = now
        self.updated_at = now
        self.status_at = now

    @before_event(Replace)
    def replace_dates(self):
        self.updated_at = datetime.now(tz=timezone.utc)


class PDFDiffTask(BaseTask):
    key: str

    class Settings:
        union_doc = TaskLog


class LineageTask(BaseTask):
    site_id: PydanticObjectId
    reprocess: bool = False

    class Settings:
        union_doc = TaskLog
