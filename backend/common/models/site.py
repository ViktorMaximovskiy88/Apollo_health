from datetime import datetime
from pydantic import BaseModel, HttpUrl
from backend.common.models.base_document import BaseDocument


class NewSite(BaseModel):
    name: str
    base_url: HttpUrl
    scrape_method: str
    tags: list[str] = []
    cron: str


class UpdateSite(BaseModel):
    name: str | None = None
    base_url: HttpUrl | None = None
    scrape_method: str | None = None
    tags: list[str] | None = None
    cron: str | None = None
    disabled: bool | None = None
    last_run_time: datetime | None = None


class Site(BaseDocument, NewSite):
    disabled: bool
    last_status: str | None = None
    last_run_time: datetime | None = None
