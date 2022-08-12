from beanie import PydanticObjectId, UnionDoc
from pydantic import BaseModel

from backend.common.models.base_document import BaseDocument
from backend.common.models.shared import FileMetadata, Location


class LinkTaskLog(UnionDoc):
    class Settings:
        name = "LinkTaskLog"


class ValidResponse(BaseModel):
    proxy_url: str | None
    content_length: int | None
    content_type: str | None
    status: int


class InvalidResponse(BaseModel):
    proxy_url: str | None
    status: int
    message: str | None


class LinkTask(BaseDocument):
    site_id: PydanticObjectId
    scrape_task_id: PydanticObjectId


class LinkBaseTask(LinkTask):
    base_url: str
    valid_response: ValidResponse | None
    invalid_responses: list[InvalidResponse] = []

    class Settings:
        union_doc = LinkTaskLog


class LinkRetrievedTask(LinkTask):
    file_metadata: FileMetadata | None
    location: Location
    invalid_responses: list[InvalidResponse] = []
    valid_response: ValidResponse | None
    retrieved_document_id: PydanticObjectId | None

    class Settings:
        union_doc = LinkTaskLog


#  temp until i cleanse the downloadcontext
def link_retrieved_task_from_download(download, scrape_task):
    return LinkRetrievedTask(
        scrape_task_id=scrape_task.id,
        site_id=scrape_task.site_id,
        location=Location(
            url=download.metadata.resource_value,
            **download.metadata.dict(),
        ),
    )
