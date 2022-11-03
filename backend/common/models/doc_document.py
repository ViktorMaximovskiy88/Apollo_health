from datetime import datetime
from uuid import UUID

import pymongo
from beanie import Indexed, PydanticObjectId
from pydantic import Field

from backend.common.core.enums import ApprovalStatus, LangCode
from backend.common.models.base_document import BaseDocument, BaseModel
from backend.common.models.document_mixins import DocumentMixins
from backend.common.models.shared import (
    DocDocumentLocation,
    DocDocumentLocationView,
    IndicationTag,
    LockableDocument,
    TaskLock,
    TherapyTag,
    UpdateIndicationTag,
    UpdateTherapyTag,
)


class BaseDocDocument(BaseModel):
    retrieved_document_id: Indexed(PydanticObjectId)  # type: ignore
    classification_status: Indexed(str) = ApprovalStatus.PENDING  # type: ignore
    family_status: Indexed(str) = ApprovalStatus.PENDING  # type: ignore
    content_extraction_status: Indexed(str) = ApprovalStatus.PENDING  # type: ignore

    # Global Status Field, status: APPROVED means doc is ready for downstream use
    status: Indexed(str) = ApprovalStatus.PENDING  # type: ignore

    classification_hold_info: list[str] = []
    extraction_hold_info: list[str] = []
    family_hold_info: list[str] = []

    classification_lock: TaskLock | None = None

    name: str
    checksum: str
    file_extension: str | None = None
    text_checksum: str | None = None
    lang_code: LangCode | None = None

    # Document Type
    document_type: str | None = None
    doc_type_confidence: float | None = None
    internal_document: bool | None = None

    document_family_id: PydanticObjectId | None = None
    previous_par_id: UUID | None = None

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
    first_collected_date: Indexed(datetime, pymongo.DESCENDING) | None = None
    last_collected_date: Indexed(datetime, pymongo.DESCENDING) | None = None

    # Manual/Calculated Dates
    final_effective_date: Indexed(datetime, pymongo.DESCENDING) | None = None  # type: ignore
    end_date: datetime | None = None

    # Lineage
    lineage_id: PydanticObjectId | None = None
    previous_doc_doc_id: Indexed(PydanticObjectId) | None = None  # type: ignore
    is_current_version: bool = False

    therapy_tags: list[TherapyTag] = []
    indication_tags: list[IndicationTag] = []

    translation_id: PydanticObjectId | None = None
    content_extraction_task_id: PydanticObjectId | None = None

    compare_create_time: datetime | None = None

    tags: list[str] = []


class DocDocument(BaseDocument, BaseDocDocument, LockableDocument, DocumentMixins):
    locations: list[DocDocumentLocation] = []

    def for_site(self, site_id: PydanticObjectId):
        location = self.get_site_location(site_id)
        copy = self.dict()
        copy.pop("first_collected_date")
        copy.pop("last_collected_date")
        return SiteDocDocument(_id=self.id, **copy, **location.dict())

    class Settings:
        indexes = [
            [("locations.site_id", pymongo.ASCENDING)],
            [("locks.user_id", pymongo.ASCENDING)],
        ]


class DocDocumentView(DocDocument):
    locations: list[DocDocumentLocationView] = []


class SiteDocDocument(BaseDocDocument, DocDocumentLocation):
    id: PydanticObjectId = Field(None, alias="_id")


class DocDocumentLimitTags(DocDocument):
    class Collection:
        name = "DocDocument"

    class Settings:
        projection = {"therapy_tags": {"$slice": 10}, "indication_tags": {"$slice": 10}}


class UpdateDocDocument(BaseModel, DocumentMixins):
    name: str | None = None
    document_type: str | None = None
    lang_code: LangCode | None = None
    document_family_id: PydanticObjectId | None = None
    previous_par_id: UUID | None = None

    classification_status: ApprovalStatus | None = None
    classification_lock: TaskLock | None = None
    family_status: ApprovalStatus | None = None
    content_extraction_status: ApprovalStatus | None = None
    content_extraction_lock: TaskLock | None = None

    final_effective_date: datetime | None = None
    effective_date: datetime | None = None
    last_reviewed_date: datetime | None = None
    last_updated_date: datetime | None = None
    last_reviewed_date: datetime | None = None
    next_review_date: datetime | None = None
    next_update_date: datetime | None = None
    first_created_date: datetime | None = None
    first_collected_date: datetime | None = None
    last_collected_date: datetime | None = None
    published_date: datetime | None = None
    end_date: datetime | None = None

    lineage_id: PydanticObjectId | None = None
    previous_doc_doc_id: PydanticObjectId | None = None
    is_current_version: bool | None = None

    therapy_tags: list[UpdateTherapyTag] | None = None
    indication_tags: list[UpdateIndicationTag] | None = None
    tags: list[str] | None = None
    internal_document: bool | None = None
    translation_id: PydanticObjectId | None = None
    content_extraction_task_id: PydanticObjectId | None = None

    locations: list[DocDocumentLocation] | None


class ClassificationUpdateDocDocument(BaseModel):
    name: str | None = None

    therapy_tags: list[TherapyTag] | None
    indication_tags: list[IndicationTag] | None

    lineage_id: PydanticObjectId | None = None
    previous_doc_doc_id: PydanticObjectId | None = None
    is_current_version: bool | None = None

    classification_status: ApprovalStatus | None = None
    classification_hold_info: list[str] = []
    document_type: str | None = None

    lang_code: LangCode | None = None

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


class FamilyUpdateDocDocument(BaseModel):
    family_status: ApprovalStatus | None = None
    family_hold_info: list[str] | None = None
    document_family_id: PydanticObjectId | None = None
    locations: list[DocDocumentLocation] | None = None


class TranslationUpdateDocDocument(BaseModel):
    translation_id: PydanticObjectId | None = None
    content_extraction_task_id: PydanticObjectId | None = None
    content_extraction_status: ApprovalStatus | None = None
    extraction_hold_info: list[str] | None = None


PartialDocDocumentUpdate = (
    UpdateDocDocument
    | ClassificationUpdateDocDocument
    | FamilyUpdateDocDocument
    | TranslationUpdateDocDocument
)


# Deprecated
class NoFocusTherapyTag(TherapyTag):
    relevancy: float | None = None
    focus: bool | None = None


class NoFocusTherapyTagDocDocument(DocDocument):
    therapy_tags: list[NoFocusTherapyTag] = []

    class Collection:
        name = "DocDocument"
