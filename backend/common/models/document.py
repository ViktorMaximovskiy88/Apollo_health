from datetime import datetime

import pymongo
from beanie import Indexed, PydanticObjectId
from pydantic import BaseModel, Field

from backend.common.core.enums import LangCode
from backend.common.models.base_document import BaseDocument
from backend.common.models.document_mixins import DocumentMixins
from backend.common.models.shared import IndicationTag, RetrievedDocumentLocation, TherapyTag


class BaseRetrievedDocument(BaseModel):
    uploader_id: PydanticObjectId | None = None
    # scrape_task_id: Indexed(PydanticObjectId) | None = None  # type: ignore
    checksum: Indexed(str)  # type: ignore
    text_checksum: str | None = None
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
    first_collected_date: datetime | None = None
    last_collected_date: datetime | None = None
    document_type: str | None = None
    doc_type_confidence: float | None = None
    identified_dates: list[datetime] = []
    lang_code: LangCode | None = None
    file_size: int = 0
    file_extension: str | None = None
    content_type: str | None = None

    therapy_tags: list[TherapyTag] = []
    indication_tags: list[IndicationTag] = []
    doc_vectors: list[list[float]] = []

    # lineage
    lineage_id: PydanticObjectId | None = None
    previous_doc_id: PydanticObjectId | None = None
    is_current_version: bool = False


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


class SiteRetrievedDocument(BaseRetrievedDocument, RetrievedDocumentLocation):
    id: PydanticObjectId = Field(None, alias="_id")


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
    disabled: bool | None = None
    name: str | None = None
    document_type: str | None = None
    doc_type_confidence: float | None = None
    metadata: dict | None = None

    lang_code: LangCode | None = None
    file_extension: str | None = None
    content_type: str | None = None

    therapy_tags: list[TherapyTag] | None = None
    indication_tags: list[IndicationTag] | None = None

    automated_content_extraction: bool | None = None
    automated_content_extraction_class: str | None = None

    locations: list[RetrievedDocumentLocation] = []
    doc_vectors: list[list[float]] = []
    file_size: int = 0


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
