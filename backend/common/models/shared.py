from datetime import datetime

from beanie import PydanticObjectId

from backend.common.core.enums import TagUpdateStatus
from backend.common.models.base_document import BaseModel
from backend.scrapeworker.common.utils import unique_by_attr


class Location(BaseModel):
    base_url: str
    url: str
    link_text: str | None
    closest_heading: str | None
    siblings_text: str | None


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


def get_reference_tags(tags: list[TherapyTag | IndicationTag]):
    return [tag for tag in tags if not tag.focus]


def get_focus_tags(tags: list[TherapyTag | IndicationTag]):
    return [tag for tag in tags if tag.focus]


def get_unique_reference_tags(tags: list[TherapyTag | IndicationTag]):
    return unique_by_attr(get_reference_tags(tags), "code")


def get_unique_focus_tags(tags: list[TherapyTag | IndicationTag]):
    return unique_by_attr(get_focus_tags(tags), "code")
