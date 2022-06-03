from datetime import datetime
from pydantic import BaseModel, HttpUrl
from backend.common.models.base_document import BaseDocument


class ScrapeMethodConfiguration(BaseModel):
    document_extensions: list[str]
    url_keywords: list[str]


class BaseUrl(BaseModel):
    url: HttpUrl
    name: str = ""
    status: str = "ACTIVE"


class NewSite(BaseModel):
    name: str
    base_urls: list[BaseUrl] = []
    scrape_method: str
    scrape_method_configuration: ScrapeMethodConfiguration
    tags: list[str] = []
    cron: str


class UpdateSite(BaseModel):
    name: str | None = None
    base_urls: list[HttpUrl] | None = None
    scrape_method: str | None = None
    tags: list[str] | None = None
    cron: str | None = None
    disabled: bool | None = None
    last_run_time: datetime | None = None
    scrape_method_configuration: ScrapeMethodConfiguration | None = None


class Site(BaseDocument, NewSite):
    disabled: bool
    last_status: str | None = None
    last_run_time: datetime | None = None


# Deprecated
class NoScrapeConfigSite(Site):
    scrape_method_configuration: ScrapeMethodConfiguration | None = None

    class Collection:
        name = "Site"


class SingleUrlSite(NoScrapeConfigSite):
    base_url: HttpUrl

    class Collection:
        name = "Site"
