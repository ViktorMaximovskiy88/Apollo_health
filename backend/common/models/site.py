from datetime import datetime
from beanie import PydanticObjectId
from pydantic import BaseModel, HttpUrl
from backend.common.models.base_document import BaseDocument


class ScrapeMethodConfiguration(BaseModel):
    document_extensions: list[str]
    url_keywords: list[str]
    proxy_exclusions: list[PydanticObjectId] = []

class UpdateScrapeMethodConfiguration(BaseModel):
    document_extensions: list[str] | None = None
    url_keywords: list[str] | None = None
    proxy_exclusions: list[PydanticObjectId] | None = None


class BaseUrl(BaseModel):
    url: HttpUrl
    name: str = ""
    status: str = "ACTIVE"


class NewSite(BaseModel):
    name: str
    base_urls: list[BaseUrl] = []
    collection_method: str
    scrape_method: str
    scrape_method_configuration: ScrapeMethodConfiguration
    tags: list[str] = []
    cron: str


class UpdateSite(BaseModel):
    name: str | None = None
    base_urls: list[BaseUrl] | None = None
    scrape_method: str | None = None
    collection_method: str | None = None
    tags: list[str] | None = None
    cron: str | None = None
    disabled: bool | None = None
    last_run_time: datetime | None = None
    scrape_method_configuration: UpdateScrapeMethodConfiguration | None = None


class Site(BaseDocument, NewSite):
    disabled: bool
    last_status: str | None = None
    collection_method: str | None = "Automated"
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
