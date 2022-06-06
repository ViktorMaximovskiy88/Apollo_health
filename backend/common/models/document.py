from datetime import datetime
from beanie import PydanticObjectId
from pydantic import BaseModel
from backend.common.models.base_document import BaseDocument


class RetrievedDocument(BaseDocument):
    site_id: PydanticObjectId | None = None
    scrape_task_id: PydanticObjectId | None = None
    logical_document_id: PydanticObjectId | None = None
    logical_document_version: int | None = None
    collection_time: datetime | None = None
    last_seen: datetime | None = None
    url: str | None = None
    checksum: str | None = None
    disabled: bool = False
    name: str | None = None
    metadata: dict = {}
    context_metadata: dict = {}
    effective_date: datetime | None = None
    document_type: str | None = None
    doc_type_confidence: float | None = None
    identified_dates: list[datetime] = []

    automated_content_extraction: bool = False
    automated_content_extraction_class: str | None = None


class UpdateRetrievedDocument(BaseModel):
    site_id: PydanticObjectId | None = None
    effective_date: datetime | None = None
    identified_dates: list[datetime] | None = None
    scrape_task_id: PydanticObjectId | None = None
    logical_document_id: PydanticObjectId | None = None
    logical_document_version: int | None = None
    collection_time: datetime | None = None
    last_seen: datetime | None = None
    url: str | None = None
    checksum: str | None = None
    disabled: bool | None = None
    name: str | None = None
    document_type: str | None = None
    doc_type_confidence: float | None = None
    metadata: dict | None = None
    context_metadata: dict | None = None

    automated_content_extraction: bool | None = None
    automated_content_extraction_class: str | None = None
