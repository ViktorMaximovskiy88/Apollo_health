from datetime import datetime
from uuid import UUID

from beanie import Indexed, PydanticObjectId
from pydantic import BaseModel

from backend.common.core.enums import CollectionMethod, TaskStatus
from backend.common.models.base_document import BaseDocument


class HttpResponse(BaseModel):
    content_type: str
    content_length: int
    status: int


class ProxyResponse(BaseModel):
    proxy_url: str
    response: HttpResponse


class Location(BaseModel):
    base_url: str
    url: str
    link_text: str


class LinkTask(BaseModel):
    location: Location
    response: HttpResponse
    retrieved_document_id: PydanticObjectId
    proxy_respones: list[ProxyResponse]


class SiteScrapeTask(BaseDocument):
    site_id: Indexed(PydanticObjectId)  # type: ignore
    initiator_id: PydanticObjectId | None = None
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
    collection_method: str | None = CollectionMethod.Automated
    link_tasks: list[LinkTask] = []


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
    link_tasks: list[LinkTask] = []


# Deprecated
class NoDocIdScrapeTask(SiteScrapeTask):
    retrieved_document_id: None = None

    class Collection:
        name = "SiteScrapeTask"
