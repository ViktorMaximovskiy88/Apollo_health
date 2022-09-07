from datetime import datetime
from enum import Enum
from uuid import UUID

from beanie import Indexed, PydanticObjectId
from pydantic import BaseModel

from backend.common.core.enums import CollectionMethod, TaskStatus
from backend.common.models.base_document import BaseDocument
from backend.common.models.site import ScrapeMethodConfiguration


class WorkItemOption(Enum):
    FOUND = "FOUND"
    NEW_DOCUMENT = "NEW_DOCUMENT"
    NOT_FOUND = "NOT_FOUND"
    UNHANDLED = "UNHANDLED"


class WorkItem(BaseDocument):
    document_id: PydanticObjectId
    retrieved_document_id: PydanticObjectId
    selected: str = WorkItemOption.UNHANDLED
    new_doc: PydanticObjectId | None = None
    prev_doc: PydanticObjectId | None = None
    last_collected_date: datetime | None = None


class UpdateWorkItem(BaseModel):
    document_id: PydanticObjectId | None = None
    retrieved_document_id: PydanticObjectId | None = None
    selected: str | None = None
    new_doc: PydanticObjectId | None = None
    prev_doc: PydanticObjectId | None = None
    last_collected_date: datetime | None = None


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
    scrape_method_configuration: ScrapeMethodConfiguration | None = None
    work_list: list[WorkItem] = []


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
    work_list: list[WorkItem] = []


# Deprecated
class NoDocIdScrapeTask(SiteScrapeTask):
    retrieved_document_id: None = None

    class Collection:
        name = "SiteScrapeTask"
