from datetime import datetime
from uuid import UUID
from beanie import PydanticObjectId
from pydantic import BaseModel
from backend.common.models.base_document import BaseDocument
from backend.common.core.enums import ScrapeTaskStatus


class ContentExtractionTask(BaseDocument):
    site_id: PydanticObjectId | None = None
    retrieved_document_id: PydanticObjectId | None = None
    scrape_task_id: PydanticObjectId | None = None

    worker_id: UUID | None = None
    queued_time: datetime
    start_time: datetime | None = None
    end_time: datetime | None = None
    status: str = ScrapeTaskStatus.QUEUED

    extraction_count: int = 0


class UpdateContentExtractionTask(BaseModel):
    worker_id: UUID | None = None
    queued_time: datetime | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    status: str | None = None

    extraction_count: int | None = None


class ContentExtractionResult(BaseDocument):
    site_id: PydanticObjectId | None = None
    retrieved_document_id: PydanticObjectId | None = None
    scrape_task_id: PydanticObjectId | None = None
    content_extraction_task_id: PydanticObjectId | None = None

    page: int
    row: int
    first_collected_date: datetime
    result: dict = {}
