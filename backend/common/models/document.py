from datetime import datetime

from beanie import Indexed, PydanticObjectId
from pydantic import BaseModel

from backend.common.core.enums import LangCode
from backend.common.models.base_document import BaseDocument
from backend.common.models.doc_document import IndicationTag, TherapyTag


class RetrievedDocument(BaseDocument):
    site_id: PydanticObjectId | None = None
    uploader_id: PydanticObjectId | None = None
    scrape_task_id: Indexed(PydanticObjectId) | None = None  # type: ignore
    logical_document_id: PydanticObjectId | None = None
    logical_document_version: int | None = None
    first_collected_date: datetime | None = None
    last_collected_date: datetime | None = None
    url: Indexed(str)  # type: ignore
    checksum: Indexed(str)  # type: ignore
    text_checksum: str | None = None
    disabled: bool = False
    name: str
    metadata: dict = {}
    context_metadata: dict = {}
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
    base_url: str | None = None
    lang_code: LangCode | None = None
    file_extension: str | None = None
    content_type: str | None = None
    # full text is the same for checksums in the below set
    file_checksum_aliases: list[str] = list()

    therapy_tags: list[TherapyTag] = []
    indication_tags: list[IndicationTag] = []


class UpdateRetrievedDocument(BaseModel):
    site_id: PydanticObjectId | None = None
    effective_date: datetime | None = None
    end_date: datetime | None = None
    last_updated_date: datetime | None = None
    last_reviewed_date: datetime | None = None
    next_review_date: datetime | None = None
    next_update_date: datetime | None = None
    published_date: datetime | None = None
    identified_dates: list[datetime] | None = None
    scrape_task_id: PydanticObjectId | None = None
    logical_document_id: PydanticObjectId | None = None
    logical_document_version: int | None = None
    first_collected_date: datetime | None = None
    last_collected_date: datetime | None = None
    url: str | None = None
    checksum: str | None = None
    text_checksum: str | None = None
    disabled: bool | None = None
    name: str | None = None
    document_type: str | None = None
    doc_type_confidence: float | None = None
    metadata: dict | None = None
    context_metadata: dict | None = None
    lang_code: LangCode | None = None
    file_checksum_aliases: set[str] = set()

    therapy_tags: list[TherapyTag] | None = None
    indication_tags: list[IndicationTag] | None = None


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
