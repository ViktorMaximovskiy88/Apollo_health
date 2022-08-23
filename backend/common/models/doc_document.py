from datetime import datetime

from beanie import Indexed, PydanticObjectId
from pydantic import BaseModel, Field

from backend.common.core.enums import ApprovalStatus, TaskStatus
from backend.common.models.base_document import BaseDocument
from backend.common.models.document_mixins import DocumentMixins
from backend.common.models.shared import (
    DocDocumentLocation,
    IndicationTag,
    LockableDocument,
    TaskLock,
    TherapyTag,
    UpdateIndicationTag,
    UpdateTherapyTag,
)


class BaseDocDocument(BaseModel):
    retrieved_document_id: Indexed(PydanticObjectId)  # type: ignore
    classification_status: Indexed(str) = ApprovalStatus.QUEUED  # type: ignore
    content_extraction_status: Indexed(str) = ApprovalStatus.QUEUED  # type: ignore
    classification_lock: TaskLock | None = None

    name: str
    checksum: str
    file_extension: str | None = None
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
    identified_dates: list[datetime] | None = None
    first_collected_date: datetime | None = None
    last_collected_date: datetime | None = None

    # Manual/Calculated Dates
    final_effective_date: datetime | None = None
    end_date: datetime | None = None

    # Lineage
    # TODO ask about these two ...
    lineage_id: PydanticObjectId | None = None
    version: str | None = None

    therapy_tags: list[TherapyTag] = []
    indication_tags: list[IndicationTag] = []

    translation_id: PydanticObjectId | None = None
    content_extraction_task_id: PydanticObjectId | None = None

    tags: list[str] = []

    document_family_id: PydanticObjectId | None = None


class DocDocument(BaseDocument, BaseDocDocument, LockableDocument, DocumentMixins):
    locations: list[DocDocumentLocation] = []

    def for_site(self, site_id: PydanticObjectId):
        location = self.get_site_location(site_id)
        return SiteDocDocument(_id=self.id, **self.dict(), **location.dict())


class SiteDocDocument(BaseDocDocument, DocDocumentLocation):
    id: PydanticObjectId = Field(None, alias="_id")


class DocDocumentLimitTags(DocDocument):
    class Collection:
        name = "DocDocument"

    class Settings:
        projection = {"therapy_tags": {"$slice": 10}, "indication_tags": {"$slice": 10}}


class UpdateDocDocument(BaseModel, DocumentMixins):
    site_id: PydanticObjectId | None = None
    classification_status: TaskStatus = TaskStatus.QUEUED
    classification_lock: TaskLock | None = None
    name: str | None = None
    document_type: str | None = None

    final_effective_date: datetime | None = None
    effective_date: datetime | None = None
    last_reviewed_date: datetime | None = None
    last_updated_date: datetime | None = None
    last_reviewed_date: datetime | None = None
    next_review_date: datetime | None = None
    next_update_date: datetime | None = None
    first_created_date: datetime | None = None
    published_date: datetime | None = None
    end_date: datetime | None = None

    lineage_id: PydanticObjectId | None = None
    version: str | None = None

    therapy_tags: list[UpdateTherapyTag] | None = None
    indication_tags: list[UpdateIndicationTag] | None = None
    tags: list[str] | None = None

    translation_id: PydanticObjectId | None = None
    content_extraction_task_id: PydanticObjectId | None = None
    content_extraction_status: ApprovalStatus = ApprovalStatus.QUEUED
    content_extraction_lock: TaskLock | None = None

    document_family_id: PydanticObjectId | None = None


# Deprecated
class NoFocusTherapyTag(TherapyTag):
    relevancy: float | None = None
    focus: bool | None = None


class NoFocusTherapyTagDocDocument(DocDocument):
    therapy_tags: list[NoFocusTherapyTag] = []

    class Collection:
        name = "DocDocument"
