from datetime import datetime
from enum import Enum
from uuid import UUID

from beanie import Indexed, PydanticObjectId

from backend.common.core.enums import CollectionMethod, TaskStatus
from backend.common.models.base_document import BaseDocument, BaseModel
from backend.common.models.site import ScrapeMethodConfiguration


class WorkItemOption(str, Enum):
    FOUND = "FOUND"
    NEW_DOCUMENT = "NEW_DOCUMENT"
    NEW_VERSION = "NEW_VERSION"
    NOT_FOUND = "NOT_FOUND"
    UNHANDLED = "UNHANDLED"


class ManualWorkItem(BaseModel):
    document_id: PydanticObjectId
    retrieved_document_id: PydanticObjectId
    selected: str = WorkItemOption.UNHANDLED
    prev_doc: PydanticObjectId | None = None
    new_doc: PydanticObjectId | None = None
    action_datetime: datetime | None = None
    is_current_version: bool | None = True
    is_new: bool | None = True


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
    new_retrieved_document_ids: list[PydanticObjectId] = []
    worker_id: UUID | None = None
    error_message: str | None = None
    links_found: int = 0
    follow_links_found: int = 0
    retry_if_lost: bool = False
    collection_method: str | None = CollectionMethod.Automated
    scrape_method_configuration: ScrapeMethodConfiguration | None = None
    work_list: list[ManualWorkItem] | None = []


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
    scrape_method_configuration: ScrapeMethodConfiguration | None
    work_list: list[ManualWorkItem] = []


# Deprecated
class NoDocIdScrapeTask(SiteScrapeTask):
    retrieved_document_id: None = None

    class Collection:
        name = "SiteScrapeTask"
