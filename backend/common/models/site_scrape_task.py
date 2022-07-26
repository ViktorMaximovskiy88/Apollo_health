from datetime import datetime
from uuid import UUID

from beanie import Indexed, PydanticObjectId
from pydantic import BaseModel

from backend.common.core.enums import CollectionMethod, TaskStatus
from backend.common.models.base_document import BaseDocument
from backend.scrapeworker.common.models import Response


class ScrapedLinks(BaseModel):
    url: str
    response: Response | None = None
    related_doc_by_url: PydanticObjectId | None = None
    related_doc_by_checksum: PydanticObjectId | None = None


class SiteScrapeTask(BaseDocument):
    site_id: Indexed(PydanticObjectId)  # type: ignore
    queued_time: datetime
    start_time: datetime | None = None
    end_time: datetime | None = None
    last_active: datetime | None = None
    status: Indexed(str) = TaskStatus.QUEUED  # type: ignore
    documents_found: int = 0
    new_documents_found: int = 0
    retrieved_document_ids: list[PydanticObjectId] = []
    worker_id: UUID | None = None
    error_message: str | None = None
    links_found: int = 0
    retry_if_lost: bool = False
    collection_type: str | None = CollectionMethod.Automated
    scraped_links_log: list[ScrapedLinks] = []


class UpdateSiteScrapeTask(BaseModel):
    worker_id: UUID | None = None
    queued_time: datetime | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    status: str | None = None
    documents_found: int | None = None
    new_documents_found: int | None = None
    error_message: str | None = None
    retry_if_lost: bool | None = False


# Deprecated
class NoDocIdScrapeTask(SiteScrapeTask):
    retrieved_document_id: None = None

    class Collection:
        name = "SiteScrapeTask"
