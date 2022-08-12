from datetime import datetime

from beanie import Indexed, PydanticObjectId
from pydantic import BaseModel

from backend.common.core.enums import LangCode
from backend.common.models.base_document import BaseDocument
from backend.common.models.shared import IndicationTag, TherapyTag


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

    automated_content_extraction: bool | None = None
    automated_content_extraction_class: str | None = None


class RetrievedDocumentLocation(BaseModel):
    url: Indexed(str)  # type: ignore
    base_url: str | None = None
    link_text: str | None
    closest_header: str | None

    context_metadata: dict = {}  # TODO, un have this and just move the stuff up?

    first_collected_date: datetime | None = None
    last_collected_date: datetime | None = None

    # composite key used for 'lineage'
    site_id: PydanticObjectId | None = None
    previous_retrieved_doc_id: PydanticObjectId | None = None


class RetrievedDocument(BaseDocument):
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

    automated_content_extraction: bool = False
    automated_content_extraction_class: str | None = None

    locations: list[RetrievedDocumentLocation] = []

    async def update_for_site(
        self,
        doc_id: PydanticObjectId,
        site_id: PydanticObjectId,
        update_model: UpdateRetrievedDocument,
    ):
        # location =
        doc: RetrievedDocument = await self.get_motor_collection().update(
            {"_id": doc_id, "locations.site_id": site_id}, {"$set": update_model.dict()}
        )
        return doc


class SiteRetrievedDocument(RetrievedDocument, RetrievedDocumentLocation):
    async def get_for_site(self, doc_id: PydanticObjectId, site_id: PydanticObjectId):
        doc: SiteRetrievedDocument = await self.get(doc_id)
        return doc.for_site(site_id)

    def for_site(self, site_id: PydanticObjectId):
        location = next((x for x in self.locations if x.site_id == site_id), None)
        return SiteRetrievedDocument(**self.dict(), **location.dict())


class RetrievedDocumentLimitTags(RetrievedDocument):
    class Collection:
        name = "RetrievedDocument"

    class Settings:
        projection = {"therapy_tags": {"$slice": 10}, "indication_tags": {"$slice": 10}}


# Deprecated
class CollectionTimeRetrievedDocument(RetrievedDocument):
    collection_time: datetime | None = None

    class Collection:
        name = "RetrievedDocument"


class LastSeenRetrievedDocument(CollectionTimeRetrievedDocument):
    last_seen: datetime | None = None

    class Collection:
        name = "RetrievedDocument"
