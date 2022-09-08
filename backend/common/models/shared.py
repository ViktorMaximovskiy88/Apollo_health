from datetime import datetime

from beanie import Indexed, PydanticObjectId
from pydantic import BaseModel
from pymongo import TEXT


class LocationContext(BaseModel):
    link_text: Indexed(str, index_type=TEXT) | None
    closest_heading: Indexed(str, index_type=TEXT) | None
    siblings_text: Indexed(str, index_type=TEXT) | None
    resource_value: Indexed(str, index_type=TEXT) | None
    base_url: Indexed(str, index_type=TEXT) | None
    element_id: str | None
    playbook_context: list[dict[str, str]] = []


class LocationSimilarity(BaseModel):
    pathname: list[str] = []
    filename: list[str] = []
    element_text: list[str] = []
    heading_text: list[str] = []
    sibling_text: list[str] = []


class Location(BaseModel):
    base_url: str
    url: str
    link_text: str | None
    closest_heading: str | None


class SiteLocation(Location):
    site_id: PydanticObjectId
    first_collected_date: datetime | None = None
    last_collected_date: datetime | None = None


class RetrievedDocumentLocation(SiteLocation):

    context_metadata: LocationContext  # TODO, un have this and just move the stuff up?
    previous_retrieved_doc_id: PydanticObjectId | None = None


class DocDocumentLocation(SiteLocation):
    document_family_id: PydanticObjectId | None = None
    previous_doc_doc_id: PydanticObjectId | None = None


class DocDocumentLocationView(DocDocumentLocation):
    site_name: str | None = None


class TherapyTag(BaseModel):
    text: str
    page: int = 0
    code: str
    name: str
    score: float = 0
    focus: bool = False

    def __hash__(self):
        return hash(tuple(self.__dict__.values()))


class FileMetadata(BaseModel):
    checksum: str
    file_size: int
    mimetype: str
    file_extension: str


class IndicationTag(BaseModel):
    text: str
    code: int
    page: int = 0
    focus: bool = False

    def __hash__(self):
        return hash(tuple(self.__dict__.values()))


class UpdateTherapyTag(BaseModel):
    name: str | None = None
    text: str | None = None
    page: int | None = None
    code: str | None = None
    score: float | None = None
    focus: bool | None = None


class UpdateIndicationTag(BaseModel):
    text: str | None = None
    page: int | None = None
    code: str | None = None
    score: float | None = None
    relevancy: float | None = None


class TaskLock(BaseModel):
    work_queue_id: PydanticObjectId
    user_id: PydanticObjectId
    expires: datetime


class LockableDocument(BaseModel):
    locks: list[TaskLock] = []
