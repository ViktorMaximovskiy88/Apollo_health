from datetime import datetime

from beanie import Indexed, PydanticObjectId, View
from pydantic import BaseModel, Field

from backend.common.core.enums import ApprovalStatus, TaskStatus
from backend.common.models.base_document import BaseDocument
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

    # Manual/Calculated Dates
    final_effective_date: datetime | None = None
    end_date: datetime | None = None

    # Lineage
    # TODO ask about these two ...
    lineage_id: PydanticObjectId | None = None
    version: str | None = None

    therapy_tags: list[TherapyTag] = []
    indication_tags: list[IndicationTag] = []

    automated_content_extraction: bool = False
    automated_content_extraction_class: str | None = None
    content_extraction_task_id: PydanticObjectId | None = None

    tags: list[str] = []


class DocDocument(BaseDocument, BaseDocDocument, LockableDocument):
    locations: list[DocDocumentLocation] = []

    def for_site(self, site_id: PydanticObjectId):
        location = next((x for x in self.locations if x.site_id == site_id), None)
        return SiteDocDocument(_id=self.id, **self.dict(), **location.dict())

    def as_rollup(self):

        first_collected_date = min(
            self.locations, key=lambda location: location.first_collected_date
        )
        last_collected_date = min(self.locations, key=lambda location: location.last_collected_date)

        return DocDocumentRollup(
            **self.dict(),
            first_collected_date=first_collected_date,
            last_collected_date=last_collected_date,
        )


class DocDocumentRollup(View):
    first_collected_date: datetime | None = None
    last_collected_date: datetime | None = None


class SiteDocDocument(View):
    id: PydanticObjectId = Field(None, alias="_id")


class DocDocumentLimitTags(DocDocument):
    class Collection:
        name = "DocDocument"

    class Settings:
        projection = {"therapy_tags": {"$slice": 10}, "indication_tags": {"$slice": 10}}


class UpdateDocDocument(BaseModel):
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

    automated_content_extraction: bool = False
    automated_content_extraction_class: str | None = None
    content_extraction_task_id: PydanticObjectId | None = None
    content_extraction_status: ApprovalStatus = ApprovalStatus.QUEUED
    content_extraction_lock: TaskLock | None = None


# Deprecated
class NoFocusTherapyTag(TherapyTag):
    relevancy: float | None = None
    focus: bool | None = None


class NoFocusTherapyTagDocDocument(DocDocument):
    therapy_tags: list[NoFocusTherapyTag] = []

    class Collection:
        name = "DocDocument"
