from datetime import datetime
from uuid import UUID

from beanie import Indexed, PydanticObjectId
from pydantic import BaseModel

from backend.common.core.enums import CollectionMethod, TaskStatus
from backend.common.models.base_document import BaseDocument
from backend.scrapeworker.common.models import DownloadContext


class FileMetadata(BaseModel):
    checksum: str
    file_name: str
    file_size: int
    mimetype: str


class HttpResponse(BaseModel):
    content_disposition: str | None
    content_length: int
    content_type: str
    status: int


class ProxyResponse(BaseModel):
    proxy_url: str
    response: HttpResponse


# plus ... whatever
class Location(BaseModel):
    base_url: str
    link_text: str | None
    url: str


class LinkTask(BaseModel):
    file_metadata: FileMetadata | None
    location: Location
    proxy_respones: list[ProxyResponse] = []
    response: HttpResponse | None
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


#  temp until i cleanse the downloadcontext
def link_task_from_download(download: DownloadContext):
    return LinkTask(
        location=Location(
            url=download.metadata.href,
            base_url=download.metadata.base_url,
        ),
    )


def create_followed_link_task(
    url: str,
    base_url: str,
    link_text: str,
    content_length: str,
    content_type: str,
    status: int,
    content_disposition: str = None,
):
    return LinkTask(
        location=Location(
            url=url,
            base_url=base_url,
            link_text=link_text,
        ),
        http_response=HttpResponse(
            content_length=content_length,
            content_type=content_type,
            status=status,
            content_disposition=content_disposition,
        ),
    )


def create_scraped_link_task(
    url: str,
    base_url: str,
    link_text: str,
):
    return LinkTask(
        location=Location(
            url=url,
            base_url=base_url,
            link_text=link_text,
        ),
    )


# Deprecated
class NoDocIdScrapeTask(SiteScrapeTask):
    retrieved_document_id: None = None

    class Collection:
        name = "SiteScrapeTask"
