from datetime import datetime
from beanie import Indexed, PydanticObjectId
from pydantic import BaseModel
from backend.common.models.base_document import BaseDocument
from backend.common.core.enums import LangCode
from backend.common.models.doc_document import IndicationTag, TherapyTag


class RetrievedDocument(BaseDocument):
    site_id: PydanticObjectId | None = None
    scrape_task_id: Indexed(PydanticObjectId) | None = None  # type: ignore
    logical_document_id: PydanticObjectId | None = None
    logical_document_version: int | None = None
    first_collected_date: datetime | None = None
    last_collected_date: datetime | None = None
    url: str | None = None
    checksum: Indexed(str)  # type: ignore
    disabled: bool = False
    name: str
    metadata: dict = {}
    context_metadata: dict = {}
    effective_date: datetime | None = None
    end_date: datetime | None = None
    last_updated_date: datetime | None = None
    next_review_date: datetime | None = None
    next_update_date: datetime | None = None
    published_date: datetime | None = None
    document_type: str | None = None
    doc_type_confidence: float | None = None
    identified_dates: list[datetime] = []
    base_url: str | None = None
    lang_code: LangCode | None = None
    file_extension: str | None = None

    therapy_tags: list[TherapyTag] = []
    indication_tags: list[IndicationTag] = []

    automated_content_extraction: bool = False
    automated_content_extraction_class: str | None = None


class UpdateRetrievedDocument(BaseModel):
    site_id: PydanticObjectId | None = None
    effective_date: datetime | None = None
    end_date: datetime | None = None
    last_updated_date: datetime | None = None
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
    disabled: bool | None = None
    name: str | None = None
    document_type: str | None = None
    doc_type_confidence: float | None = None
    metadata: dict | None = None
    context_metadata: dict | None = None
    lang_code: LangCode | None = None
    file_extension: str | None = None

    therapy_tags: list[TherapyTag] | None = None
    indication_tags: list[IndicationTag] | None = None

    automated_content_extraction: bool | None = None
    automated_content_extraction_class: str | None = None


# Deprecated
class CollectionTimeRetrievedDocument(RetrievedDocument):
    collection_time: datetime | None = None

    class Collection:
        name = "RetrievedDocument"


class LastSeenRetrievedDocument(CollectionTimeRetrievedDocument):
    last_seen: datetime | None = None

    class Collection:
        name = "RetrievedDocument"
