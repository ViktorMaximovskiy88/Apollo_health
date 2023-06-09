from datetime import datetime

import pymongo
from beanie import Indexed, PydanticObjectId
from pydantic import Field

from backend.common.core.enums import LangCode
from backend.common.models.base_document import BaseDocument, BaseModel
from backend.common.models.document_mixins import DocumentMixins
from backend.common.models.shared import (
    DocTypeMatch,
    IndicationTag,
    RetrievedDocumentLocation,
    TherapyTag,
)


class BaseRetrievedDocument(BaseModel):
    uploader_id: PydanticObjectId | None = None
    # scrape_task_id: Indexed(PydanticObjectId) | None = None  # type: ignore
    checksum: Indexed(str)  # type: ignore
    text_checksum: Indexed(str) | None = None
    content_checksum: Indexed(str) | None = None
    disabled: bool = False
    name: str
    metadata: dict = {}
    effective_date: datetime | None = None
    end_date: datetime | None = None
    last_updated_date: datetime | None = None
    last_reviewed_date: datetime | None = None
    next_review_date: datetime | None = None
    next_update_date: datetime | None = None
    published_date: datetime | None = None
    first_collected_date: Indexed(datetime) | None = None
    last_collected_date: datetime | None = None
    document_type: str | None = None
    doc_type_confidence: float | None = None
    doc_type_match: DocTypeMatch | None
    identified_dates: list[datetime] = []
    lang_code: LangCode | None = None
    file_size: int = 0
    file_extension: str | None = None
    content_type: str | None = None

    therapy_tags: list[TherapyTag] = []
    indication_tags: list[IndicationTag] = []
    doc_vectors: list[list[float]] = []
    token_count: int = 0
    priority: int = 0
    is_searchable: bool = False

    # lineage
    lineage_id: PydanticObjectId | None = None
    previous_doc_id: PydanticObjectId | None = None
    is_current_version: bool = False
    lineage_confidence: float = 0


class SiteRetrievedDocument(BaseRetrievedDocument, RetrievedDocumentLocation):
    id: PydanticObjectId = Field(None, alias="_id")


class RetrievedDocument(BaseDocument, BaseRetrievedDocument, DocumentMixins):
    locations: list[RetrievedDocumentLocation] = []

    def for_site(self, site_id: PydanticObjectId):
        location = self.get_site_location(site_id)
        copy = self.dict()
        copy.pop("first_collected_date")
        copy.pop("last_collected_date")
        return SiteRetrievedDocument(_id=self.id, **copy, **location.dict())

    class Settings:
        indexes = [[("locations.site_id", pymongo.ASCENDING)]]


class UploadedDocument(BaseRetrievedDocument, RetrievedDocumentLocation):
    add_new_document: bool | None = None  # If adding new doc clicked from work item.
    upload_new_version_for_id: str | None = None  # If adding new version, this is original doc id.
    prev_location_site_id: str | None = None  # If same location but from different site, site_id.
    prev_location_doc_id: str | None = None  # If same location but from different site, doc_id.
    # Fields used when populating doc_doc pair.
    internal_document: bool
    first_created_date: datetime | None = None
    exists_on_this_site: bool | None = False


class UpdateRetrievedDocument(BaseModel, DocumentMixins):
    id: PydanticObjectId = Field(None, alias="_id")
    effective_date: datetime | None = None
    end_date: datetime | None = None
    last_updated_date: datetime | None = None
    last_reviewed_date: datetime | None = None
    next_review_date: datetime | None = None
    next_update_date: datetime | None = None
    published_date: datetime | None = None
    identified_dates: list[datetime] | None = None
    first_collected_date: datetime | None = None
    last_collected_date: datetime | None = None
    checksum: str | None = None
    text_checksum: str | None = None
    content_checksum: str | None = None
    disabled: bool | None = None
    name: str | None = None
    document_type: str | None = None
    doc_type_confidence: float | None = None
    doc_type_match: DocTypeMatch | None
    metadata: dict | None = None

    lang_code: LangCode | None = None
    file_extension: str | None = None
    content_type: str | None = None

    therapy_tags: list[TherapyTag] | None = None
    indication_tags: list[IndicationTag] | None = None
    priority: int | None = None

    automated_content_extraction: bool | None = None
    automated_content_extraction_class: str | None = None

    locations: list[RetrievedDocumentLocation] = []
    doc_vectors: list[list[float]] = []
    file_size: int = 0
    token_count: int | None = None
    is_searchable: bool = False


class RetrievedDocumentLimitTags(RetrievedDocument):
    class Collection:
        name = "RetrievedDocument"

    class Settings:
        projection = {"therapy_tags": {"$slice": 10}, "indication_tags": {"$slice": 10}}


# Deprecated
class NoFocusTherapyTag(TherapyTag):
    relevancy: float | None = None
    focus: bool | None = None


class NoFocusTherapyTagRetDocument(RetrievedDocument):
    therapy_tags: list[NoFocusTherapyTag] = []

    class Collection:
        name = "RetrievedDocument"


class CollectionTimeRetrievedDocument(NoFocusTherapyTagRetDocument):
    collection_time: datetime | None = None

    class Collection:
        name = "RetrievedDocument"


class LastSeenRetrievedDocument(CollectionTimeRetrievedDocument):
    last_seen: datetime | None = None

    class Collection:
        name = "RetrievedDocument"
