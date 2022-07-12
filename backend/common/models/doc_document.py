from datetime import datetime
from beanie import Indexed, PydanticObjectId
from pydantic import BaseModel
from backend.common.core.enums import LangCode, TaskStatus
from backend.common.models.base_document import BaseDocument


class TherapyTag(BaseModel):
    text: str
    page: int
    code: str
    score: float
    relevancy: float


class IndicationTag(BaseModel):
    text: str
    code: int


class TaskLock(BaseModel):
    work_queue_id: PydanticObjectId
    user_id: PydanticObjectId
    expires: datetime


class DocDocument(BaseDocument):
    site_id: Indexed(PydanticObjectId)  # type: ignore
    retrieved_document_id: PydanticObjectId
    classification_status: TaskStatus = TaskStatus.QUEUED
    classification_lock: TaskLock | None = None

    name: str
    checksum: str

    # Document Type
    document_type: str | None = None
    doc_type_confidence: float | None = None

    # Extracted Dates
    effective_date: datetime | None = None
    last_reviewed_date: datetime | None = None
    last_updated_date: datetime | None = None
    next_review_date: datetime | None = None
    next_update_date: datetime | None = None
    first_created_date: datetime | None = None
    published_date: datetime | None = None

    # Manual/Calculated Dates
    final_effective_date: datetime | None = None
    end_date: datetime | None = None

    first_collected_date: datetime | None = None
    last_collected_date: datetime | None = None

    # Lineage
    lineage_id: PydanticObjectId | None = None
    version: str | None = None

    # URLs
    url: str | None
    base_url: str | None
    link_text: str | None

    lang_code: LangCode | None

    therapy_tags: list[TherapyTag] = []
    indication_tags: list[IndicationTag] = []

    automated_content_extraction: bool = False
    automated_content_extraction_class: str | None = None

    tags: list[str] = []


class UpdateTherapyTag(BaseModel):
    text: str | None = None
    page: int | None = None
    code: str | None = None
    score: float | None = None
    relevancy: float | None = None


class UpdateIndicationTag(BaseModel):
    text: str | None = None
    page: int | None = None
    code: str | None = None
    score: float | None = None
    relevancy: float | None = None


class UpdateDocDocument(BaseDocument):
    classification_status: TaskStatus = TaskStatus.QUEUED
    classification_lock: TaskLock | None = None
    name: str | None = None
    document_type: str | None = None

    effective_date: datetime | None = None
    last_reviewed_date: datetime | None = None
    last_updated_date: datetime | None = None
    next_review_date: datetime | None = None
    next_update_date: datetime | None = None
    first_created_date: datetime | None = None
    published_date: datetime | None = None

    end_date: datetime | None = None

    first_collected_date: datetime | None = None
    last_collected_date: datetime | None = None

    lineage_id: PydanticObjectId | None = None
    version: str | None = None

    lang_code: LangCode | None

    therapy_tags: list[UpdateTherapyTag] | None = None
    indication_tags: list[UpdateIndicationTag] | None = None

    automated_content_extraction: bool = False
    automated_content_extraction_class: str | None = None
    tags: list[str] | None = None
