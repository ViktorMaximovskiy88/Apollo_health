from datetime import datetime
from uuid import UUID

import pymongo
from beanie import Indexed, PydanticObjectId
from beanie.odm.queries.find import FindOne
from pydantic import Field

from backend.common.core.enums import ApprovalStatus, LangCode
from backend.common.models.base_document import BaseDocument, BaseModel
from backend.common.models.document_family import DocumentFamily
from backend.common.models.document_mixins import DocumentMixins
from backend.common.models.pipeline import DocPipelineStages
from backend.common.models.shared import (
    DocDocumentLocation,
    DocDocumentLocationView,
    DocTypeMatch,
    IndicationTag,
    LockableDocument,
    TaskLock,
    TherapyTag,
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

    name: Indexed(str)  # type: ignore # Used when sorting asc or desc
    checksum: Indexed(str)  # type: ignore
    file_extension: str | None = None
    text_checksum: Indexed(str) | None = None  # type: ignore
    content_checksum: Indexed(str) | None = None  # type: ignore

    lang_code: LangCode | None = None

    # Document Type
    document_type: Indexed(str) | None = None  # type: ignore
    doc_type_confidence: float | None = None
    doc_type_match: DocTypeMatch | None = None
    internal_document: bool | None = None

    document_family_id: Indexed(PydanticObjectId) | None = None  # type: ignore
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
    first_collected_date: datetime | None = None  # type: ignore
    last_collected_date: Indexed(datetime, pymongo.DESCENDING) | None = None  # type: ignore

    # Manual/Calculated Dates
    final_effective_date: datetime | None = None
    end_date: datetime | None = None

    # Lineage
    lineage_id: Indexed(PydanticObjectId) | None = None
    previous_doc_doc_id: Indexed(PydanticObjectId) | None = None  # type: ignore
    is_current_version: bool = False
    lineage_confidence: float = 0

    therapy_tags: list[TherapyTag] = []
    indication_tags: list[IndicationTag] = []

    translation_id: PydanticObjectId | None = None
    content_extraction_task_id: PydanticObjectId | None = None

    compare_create_time: datetime | None = None

    tags: list[str] = []
    pipeline_stages: DocPipelineStages | None = None

    # from rt doc, lets just do these now...
    # TODO if we gen analysis doc earlier, this doesnt have to live here
    doc_vectors: list[list[float]] = []
    file_size: int = 0
    token_count: int = 0

    user_edited_fields: list[str] = []
    priority: Indexed(int, pymongo.DESCENDING) = 0  # type: ignore
    is_searchable: bool = False

    hold_type: str | None = None


class DocDocument(BaseDocument, BaseDocDocument, LockableDocument, DocumentMixins):
    locations: list[DocDocumentLocation] = []

    @property
    def next_doc_document(self) -> FindOne["DocDocument"]:
        return DocDocument.find_one({"previous_doc_doc_id": self.id})

    def for_site(self, site_id: PydanticObjectId):
        location = self.get_site_location(site_id)
        copy = self.dict()
        copy.pop("first_collected_date")
        copy.pop("last_collected_date")
        return SiteDocDocument(_id=self.id, **copy, **location.dict())

    def s3_doc_key(self):
        return f"{self.checksum}.{self.file_extension}"

    def s3_text_key(self):
        return f"{self.text_checksum}.txt"

    def set_unedited_attr(self, attr, value):
        if attr not in self.user_edited_fields:
            setattr(self, attr, value)

    # has _any_ edits from attrs
    def has_user_edit(self, *attrs):
        for attr in attrs:
            if attr in self.user_edited_fields:
                return True
        return False

    def has_date_user_edits(self):
        return self.has_user_edit(
            "effective_date",
            "end_date",
            "last_updated_date",
            "last_reviewed_date",
            "next_review_date",
            "next_update_date",
            "published_date",
        )

    def has_tag_user_edits(self):
        return self.has_user_edit("therapy_tags", "indication_tags")

    def get_stage_version(self, stage_name):
        if not self.pipeline_stages:
            return 0
        stage = getattr(self.pipeline_stages, stage_name)
        if not stage:
            return 0
        return stage.version

    def process_tag_changes(
        self,
        new_therapy_tags,
        new_indication_tags,
        pending_therapy_tags,
        pending_indication_tags,
    ):
        # if not edited for therapy_tags or indication_tags just wholesale assign
        # if edited for therapy_tags or indication_tags just append diff
        # the tag differ doesnt account for removal? is that real?

        has_therapy_tag_updates = False
        if new_therapy_tags:
            if self.classification_status == ApprovalStatus.APPROVED or self.has_user_edit(
                "therapy_tags"
            ):
                self.therapy_tags += new_therapy_tags
                has_therapy_tag_updates = True
            else:
                has_therapy_tag_updates = (
                    len(pending_therapy_tags) != len(self.therapy_tags) or len(new_therapy_tags) > 0
                )
                self.therapy_tags = pending_therapy_tags

        has_indication_tag_updates = False
        if new_indication_tags:
            if self.classification_status == ApprovalStatus.APPROVED or self.has_user_edit(
                "indication_tags"
            ):
                has_indication_tag_updates = True
                self.indication_tags += new_indication_tags
            else:
                has_indication_tag_updates = (
                    len(pending_indication_tags) != len(self.indication_tags)
                    or len(new_indication_tags) > 0
                )
                self.indication_tags = pending_indication_tags

        return has_therapy_tag_updates, has_indication_tag_updates

    class Settings:
        indexes = [
            [
                ("priority", pymongo.DESCENDING),
                ("classification_status", pymongo.ASCENDING),
                ("final_effective_date", pymongo.ASCENDING),
                ("first_collected_date", pymongo.ASCENDING),
                ("hold_type", pymongo.ASCENDING),
            ],
            [
                ("priority", pymongo.DESCENDING),
                ("classification_status", pymongo.ASCENDING),
                ("family_status", pymongo.ASCENDING),
                ("final_effective_date", pymongo.ASCENDING),
                ("first_collected_date", pymongo.ASCENDING),
                ("hold_type", pymongo.ASCENDING),
            ],
            [
                ("priority", pymongo.DESCENDING),
                ("classification_status", pymongo.ASCENDING),
                ("family_status", pymongo.ASCENDING),
                ("content_extraction_status", pymongo.ASCENDING),
                ("final_effective_date", pymongo.ASCENDING),
                ("first_collected_date", pymongo.ASCENDING),
                ("hold_type", pymongo.ASCENDING),
            ],
            [("locations.site_id", pymongo.ASCENDING)],
            [("locations.link_text", pymongo.ASCENDING)],
            [("locations.url", pymongo.ASCENDING)],
            [("locks.user_id", pymongo.ASCENDING)],
            [("locations.payer_family_id", pymongo.ASCENDING)],
            [("therapy_tags.code", pymongo.ASCENDING), ("therapy_tags.focus", pymongo.ASCENDING)],
            [("indication_tags.code", pymongo.ASCENDING)],
            [("name", pymongo.TEXT), ("locations.link_text", pymongo.TEXT)],
        ]


class DocDocumentView(DocDocument):
    locations: list[DocDocumentLocationView] = []
    document_family: DocumentFamily | None = None


class SiteDocDocument(BaseDocDocument, DocDocumentLocation):
    id: PydanticObjectId = Field(None, alias="_id")


class DocDocumentLimitTags(DocDocument):
    class Collection:
        name = "DocDocument"

    class Settings:
        projection = {
            "therapy_tags": {"$slice": 10},
            "indication_tags": {"$slice": 10},
            # "doc_vectors": 0, cannot mix exclusion and inclusion.
            "retrieved_document_id": 1,
            "name": 1,
            "checksum": 1,
            "locations": {
                "link_text": 1,
                "base_url": 1,
                "url": 1,
                "site_id": 1,
                "payer_family_id": 1,
            },
            "checksum": 1,
            "final_effective_date": 1,
            "document_type": 1,
            "document_family_id": 1,
            "status": 1,
            "classification_status": 1,
            "family_status": 1,
            "content_extraction_status": 1,
            "first_collected_date": 1,
            "last_collected_date": 1,
            "is_current_version": 1,
            "priority": 1,
        }


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

    therapy_tags: list[TherapyTag] | None = None
    indication_tags: list[IndicationTag] | None = None
    tags: list[str] | None = None
    internal_document: bool | None = None
    translation_id: PydanticObjectId | None = None
    content_extraction_task_id: PydanticObjectId | None = None

    locations: list[DocDocumentLocation] | None = None

    user_edited_fields: list[str] = []
    include_later_documents_in_lineage_update: bool = False
    hold_type: str | None = None


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
    include_later_documents_in_lineage_update: bool = False
    hold_type: str | None = None


class FamilyUpdateDocDocument(BaseModel):
    family_status: ApprovalStatus | None = None
    family_hold_info: list[str] | None = None
    document_family_id: PydanticObjectId | None = None
    locations: list[DocDocumentLocation] | None = None
    hold_type: str | None = None


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


class BulkUpdateRequest(BaseModel):
    ids: list[PydanticObjectId]
    update: UpdateDocDocument
    site_id: PydanticObjectId | None
    payer_family_id: PydanticObjectId | None
    all_sites: bool = False


class BulkUpdateResponse(BaseModel):
    count_success: int
    count_error: int
    errors: list[str]


class IdOnlyDocument(BaseModel):
    id: PydanticObjectId = Field(None, alias="_id")
