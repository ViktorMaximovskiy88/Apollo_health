from datetime import datetime
from enum import Enum

from beanie import PydanticObjectId

from backend.common.core.enums import DocumentType, TagUpdateStatus
from backend.common.models.base_document import BaseModel
from backend.common.models.payer_family import PayerFamily
from backend.scrapeworker.common.utils import unique_by_attr


class TherapyTag(BaseModel):
    text: str
    page: int = 0
    code: str
    name: str
    score: float = 0
    focus: bool = False
    key: bool = False
    rxcui: str | None = None
    update_status: TagUpdateStatus | None = None
    text_area: tuple[int, int] | None = None

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
    key: bool = False
    update_status: TagUpdateStatus | None = None
    text_area: tuple[int, int] | None = None

    def __hash__(self):
        return hash(tuple(self.__dict__.values()))


class UpdateTherapyTag(BaseModel):
    text: str | None = None
    page: int | None = None
    code: str | None = None
    name: str | None = None
    score: float | None = None
    focus: bool | None = None
    update_status: TagUpdateStatus | None = None
    text_area: tuple[int, int] | None = None


class UpdateIndicationTag(BaseModel):
    text: str | None = None
    code: str | None = None
    page: int | None = None
    focus: bool | None = None
    update_status: TagUpdateStatus | None = None
    text_area: tuple[int, int] | None = None


class TaskLock(BaseModel):
    work_queue_id: PydanticObjectId
    user_id: PydanticObjectId
    expires: datetime


class LockableDocument(BaseModel):
    locks: list[TaskLock] = []


class Location(BaseModel):
    base_url: str
    url: str
    link_text: str | None = None
    closest_heading: str | None = None
    siblings_text: str | None = None
    url_therapy_tags: list[TherapyTag] = []
    url_indication_tags: list[IndicationTag] = []
    link_therapy_tags: list[TherapyTag] = []
    link_indication_tags: list[IndicationTag] = []


class SiteLocation(Location):
    site_id: PydanticObjectId
    first_collected_date: datetime | None = None
    last_collected_date: datetime | None = None


class RetrievedDocumentLocation(SiteLocation):
    context_metadata: dict = {}


class DocDocumentLocation(SiteLocation):
    payer_family_id: PydanticObjectId | None = None


class DocDocumentLocationView(DocDocumentLocation):
    site_name: str | None = None
    payer_family: PayerFamily | None = None


class MatchSource(str, Enum):
    DocText = "DocText"
    LinkText = "LinkText"
    Filename = "Filename"
    Name = "Name"


class DocTypeMatch(BaseModel):
    document_type: DocumentType
    match_source: MatchSource
    confidence: float
    rule_name: str
    texts: list[str] = []


def get_reference_tags(tags: list[TherapyTag] | list[IndicationTag]):
    return [tag for tag in tags if not tag.focus]


def get_focus_tags(tags: list[TherapyTag] | list[IndicationTag]):
    return [tag for tag in tags if tag.focus]


def get_unique_reference_tags(tags: list[TherapyTag] | list[IndicationTag]):
    return unique_by_attr(get_reference_tags(tags), "code")


def get_unique_focus_tags(tags: list[TherapyTag] | list[IndicationTag]):
    return unique_by_attr(get_focus_tags(tags), "code")
