from datetime import datetime, timezone

from beanie import Insert, PydanticObjectId, Replace, UnionDoc, before_event

from backend.common.models.base_document import BaseDocument, BaseModel
from backend.common.models.shared import FileMetadata, Location


class LinkTaskLog(UnionDoc):
    class Settings:
        name = "LinkTaskLog"
        use_revision = False


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

    created_at: datetime | None = None
    updated_at: datetime | None = None

    @before_event(Insert)
    def insert_dates(self):
        now = datetime.now(tz=timezone.utc)
        self.created_at = now
        self.updated_at = now

    @before_event(Replace)
    def replace_dates(self):
        self.updated_at = datetime.now(tz=timezone.utc)


class LinkBaseTask(LinkTask):
    base_url: str
    valid_response: ValidResponse | None = None
    invalid_responses: list[InvalidResponse] = []

    class Settings:
        union_doc = LinkTaskLog


class LinkRetrievedTask(LinkTask):
    file_metadata: FileMetadata | None = None
    location: Location
    invalid_responses: list[InvalidResponse] = []
    valid_response: ValidResponse | None = None
    retrieved_document_id: PydanticObjectId | None = None
    error_message: str = ""

    class Settings:
        union_doc = LinkTaskLog


#  temp until i cleanse the downloadcontext
def link_retrieved_task_from_download(download, scrape_task):
    url = (
        download.metadata.resource_value
        if download.metadata.resource_value
        else download.request.url
    )
    return LinkRetrievedTask(
        scrape_task_id=scrape_task.id,
        site_id=scrape_task.site_id,
        location=Location(
            url=url,
            **download.metadata.dict(),
        ),
    )
