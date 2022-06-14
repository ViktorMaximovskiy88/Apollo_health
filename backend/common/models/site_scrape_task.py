from datetime import datetime
from uuid import UUID
from beanie import PydanticObjectId
from pydantic import BaseModel
from backend.common.models.base_document import BaseDocument


class SiteScrapeTask(BaseDocument):
    site_id: PydanticObjectId
    queued_time: datetime
    start_time: datetime | None = None
    end_time: datetime | None = None
    last_active: datetime | None = None
    status: str = "QUEUED"
    documents_found: int = 0
    new_documents_found: int = 0
    worker_id: UUID | None = None
    error_message: str | None = None
    links_found: int = 0


class UpdateSiteScrapeTask(BaseModel):
    worker_id: UUID | None = None
    queued_time: datetime | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    status: str | None = None
    documents_found: int | None = None
    new_documents_found: int | None = None
    error_message: str | None = None
