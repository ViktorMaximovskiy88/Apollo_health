from datetime import datetime

from beanie import Indexed, PydanticObjectId
from pydantic import BaseModel

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


class DocDocument(BaseDocument, LockableDocument):
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

    locations: list[DocDocumentLocation] = []

    async def update_for_site(self, doc_id: PydanticObjectId, site_id: PydanticObjectId):
        pass


class SiteDocDocument(DocDocument, DocDocumentLocation):
    def get_for_site(self, doc_id: PydanticObjectId, site_id: PydanticObjectId):
        doc: SiteDocDocument = self.get(doc_id)
        return doc.for_site(site_id)

    def for_site(site_id: PydanticObjectId, doc: DocDocument):
        location = next((x for x in doc.locations if x.site_id == site_id), None)
        # TODO handle none case
        return SiteDocDocument(**doc.dict(), **location.dict())


class DocDocumentLimitTags(DocDocument):
    class Settings:
        projection = {"therapy_tags": {"$slice": 10}, "indication_tags": {"$slice": 10}}


class UpdateDocDocument(BaseModel):
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


def calc_final_effective_date(doc: DocDocument) -> datetime:
    computeFromFields = []
    if doc.effective_date:
        computeFromFields.append(doc.effective_date)
    if doc.last_reviewed_date:
        computeFromFields.append(doc.last_reviewed_date)
    if doc.last_updated_date:
        computeFromFields.append(doc.last_updated_date)

    final_effective_date = (
        max(computeFromFields) if len(computeFromFields) > 0 else doc.last_collected_date
    )

    return final_effective_date
