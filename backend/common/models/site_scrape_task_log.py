from beanie import PydanticObjectId, UnionDoc
from pydantic import BaseModel

from backend.common.models.base_document import BaseDocument
from backend.common.models.site import ScrapeMethodConfiguration


class SiteScrapeTaskLog(UnionDoc):
    class Settings:
        name = "site_scrape_task_log"


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


class Location(BaseModel):
    base_url: str
    url: str
    link_text: str | None
    closest_header: str | None


class LinkTask(BaseDocument):
    site_id: PydanticObjectId
    site_scrape_task_id: PydanticObjectId


class LinkBaseTask(LinkTask):
    base_url: str
    scrape_method_configuration: ScrapeMethodConfiguration
    valid_response: ValidResponse | None
    invalid_responses: list[InvalidResponse] = []


class LinkRetrievedTask(LinkTask):
    file_metadata: FileMetadata | None
    location: Location
    invalid_responses: list[InvalidResponse] = []
    valid_response: ValidResponse | None
    retrieved_document_id: PydanticObjectId | None


#  temp until i cleanse the downloadcontext
def link_retrieved_task_from_download(download):
    return LinkRetrievedTask(
        location=Location(
            url=download.metadata.href,
            **download.metadata.dict(),
        ),
    )
