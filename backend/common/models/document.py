from datetime import datetime

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
    document_type: str | None = None
    doc_type_confidence: float | None = None
    identified_dates: list[datetime] = []
    lang_code: LangCode | None = None
    file_extension: str | None = None
    content_type: str | None = None
    # full text is the same for checksums in the below set
    file_checksum_aliases: list[str] = list()

    therapy_tags: list[TherapyTag] = []
    indication_tags: list[IndicationTag] = []


class RetrievedDocument(BaseDocument, BaseRetrievedDocument, DocumentMixins):
    locations: list[RetrievedDocumentLocation] = []

    def for_site(self, site_id: PydanticObjectId):
        location = self.get_site_location(site_id)
        return SiteRetrievedDocument(_id=self.id, **self.dict(), **location.dict())


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

    file_checksum_aliases: set[str] = set()

    therapy_tags: list[TherapyTag] | None = None
    indication_tags: list[IndicationTag] | None = None

    automated_content_extraction: bool | None = None
    automated_content_extraction_class: str | None = None

    locations: list[RetrievedDocumentLocation] = []


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
