from datetime import datetime

from beanie import PydanticObjectId
from pydantic import BaseModel


class FileMetadata(BaseModel):
    checksum: str
    file_size: int
    mimetype: str
    file_extension: str


class Location(BaseModel):
    base_url: str
    url: str
    link_text: str | None
    closest_header: str | None


class SiteLocation(Location):
    site_id: PydanticObjectId


class TherapyTag(BaseModel):
    text: str
    page: int = 0
    code: str
    name: str
    score: float = 0
    relevancy: float = 0

    def __hash__(self):
        return hash(tuple(self.__dict__.values()))


class IndicationTag(BaseModel):
    text: str
    code: int
    page: int = 0

    def __hash__(self):
        return hash(tuple(self.__dict__.values()))


class UpdateTherapyTag(BaseModel):
    name: str | None = None
    text: str | None = None
    page: int | None = None
    code: str | None = None
    score: float | None = None
    relevancy: float | None = None


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
