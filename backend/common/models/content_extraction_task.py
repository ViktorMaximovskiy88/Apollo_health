from datetime import datetime
from uuid import UUID

from beanie import Indexed, PydanticObjectId
from pydantic import BaseModel

from backend.common.core.enums import TaskStatus
from backend.common.models.base_document import BaseDocument


class ContentExtractionTask(BaseDocument):
    site_id: PydanticObjectId | None = None
    initiator_id: PydanticObjectId | None = None
    retrieved_document_id: PydanticObjectId | None = None
    scrape_task_id: PydanticObjectId | None = None

    worker_id: UUID | None = None
    queued_time: datetime
    start_time: datetime | None = None
    end_time: datetime | None = None
    error_message: str | None = None
    status: str = TaskStatus.QUEUED

    extraction_count: int = 0
    code_column: str | None = None
    header: list[str] | None = None


class UpdateContentExtractionTask(BaseModel):
    worker_id: UUID | None = None
    queued_time: datetime | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    status: str | None = None

    extraction_count: int | None = None


class FormularyDatum(BaseModel):
    score: float = 0
    code: str | None = None
    name: str | None = None
    tier: int = 0
    pa: bool = False
    st: bool = False
    ql: bool = False
    sp: bool = False


class ContentExtractionResult(BaseDocument):
    site_id: PydanticObjectId | None = None
    retrieved_document_id: PydanticObjectId | None = None
    scrape_task_id: PydanticObjectId | None = None
    content_extraction_task_id: Indexed(PydanticObjectId) | None = None  # type: ignore
    page: int
    row: int
    first_collected_date: datetime
    result: dict = {}
    translation: FormularyDatum | None = None
