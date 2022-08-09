from datetime import datetime
from uuid import UUID

from beanie import Indexed, PydanticObjectId
from pydantic import BaseModel

from backend.common.core.enums import CollectionMethod, TaskStatus
from backend.common.models.base_document import BaseDocument


class FileMetadata(BaseModel):
    checksum: str
    file_size: int
    mimetype: str
    file_extension: str


class ValidResponse(BaseModel):
    proxy_url: str | None
    content_length: int | None
    content_type: str | None
    status: int


class InvalidResponse(BaseModel):
    proxy_url: str | None
    status: int
    message: str | None


# plus ... whatever
class Location(BaseModel):
    base_url: str
    url: str
    link_text: str | None
    closest_header: str | None


class LinkBaseTask(BaseModel):
    base_url: str
    valid_response: ValidResponse | None
    invalid_responses: list[InvalidResponse] = []


class LinkRetrievedTask(BaseModel):
    file_metadata: FileMetadata | None
    location: Location
    invalid_responses: list[InvalidResponse] = []
    valid_response: ValidResponse | None
    retrieved_document_id: PydanticObjectId | None


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
    link_source_tasks: list[LinkBaseTask] = []
    link_download_tasks: list[LinkRetrievedTask] = []


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
    link_source_tasks: list[LinkBaseTask] = []
    link_download_tasks: list[LinkRetrievedTask] = []


#  temp until i cleanse the downloadcontext
def link_retrieved_task_from_download(download):
    return LinkRetrievedTask(
        location=Location(
            url=download.metadata.href,
            **download.metadata.dict(),
        ),
    )


# Deprecated
class NoDocIdScrapeTask(SiteScrapeTask):
    retrieved_document_id: None = None

    class Collection:
        name = "SiteScrapeTask"
