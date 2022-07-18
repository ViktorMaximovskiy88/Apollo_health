from datetime import datetime
from beanie import Indexed, PydanticObjectId
from pydantic import BaseModel
from backend.common.core.enums import LangCode, TaskStatus
from backend.common.models.base_document import BaseDocument


class TherapyTag(BaseModel):
    text: str
    page: int = 0
    code: str
    name: str
    score: float = 0
    relevancy: float = 0

    def __hash__(self):
        return hash(tuple(self.__dict__.values()))


class IndicationTag(BaseModel):
    text: str
    code: int
    page: int = 0

    def __hash__(self):
        return hash(tuple(self.__dict__.values()))


class TaskLock(BaseModel):
    work_queue_id: PydanticObjectId
    user_id: PydanticObjectId
    expires: datetime


class DocDocument(BaseDocument):
    site_id: Indexed(PydanticObjectId)  # type: ignore
    retrieved_document_id: Indexed(PydanticObjectId)  # type: ignore
    classification_status: TaskStatus = TaskStatus.QUEUED
    classification_lock: TaskLock | None = None

    name: str
    checksum: str
    text_checksum: str | None = None

    # Document Type
    document_type: str | None = None
    doc_type_confidence: float | None = None

    # Extracted Dates
    effective_date: datetime | None = None
    last_reviewed_date: datetime | None = None
    last_updated_date: datetime | None = None
    last_reviewed_date: datetime | None = None
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
    content_extraction_task_id: PydanticObjectId | None = None

    tags: list[str] = []


class DocDocumentLimitTags(DocDocument):
    class Settings:
        projection = {"therapy_tags": {"$slice": 10}, "indication_tags": {"$slice": 10}}


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


class UpdateDocDocument(BaseModel):
    classification_status: TaskStatus = TaskStatus.QUEUED
    classification_lock: TaskLock | None = None
    name: str | None = None
    document_type: str | None = None
    checksum: str | None = None
    text_checksum: str | None = None

    effective_date: datetime | None = None
    last_reviewed_date: datetime | None = None
    last_updated_date: datetime | None = None
    last_reviewed_date: datetime | None = None
    next_review_date: datetime | None = None
    next_update_date: datetime | None = None
    first_created_date: datetime | None = None
    published_date: datetime | None = None

    end_date: datetime | None = None

    first_collected_date: datetime | None = None
    last_collected_date: datetime | None = None

    lineage_id: PydanticObjectId | None = None
    version: str | None = None

    lang_code: LangCode | None = None

    therapy_tags: list[UpdateTherapyTag] | None = None
    indication_tags: list[UpdateIndicationTag] | None = None

    tags: list[str] | None = None

    automated_content_extraction: bool = False
    automated_content_extraction_class: str | None = None
    content_extraction_task_id: PydanticObjectId | None = None
    content_extraction_status: TaskStatus = TaskStatus.QUEUED
    content_extraction_lock: TaskLock | None = None
