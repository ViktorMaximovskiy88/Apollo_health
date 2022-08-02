from datetime import datetime

from beanie import PydanticObjectId
from pydantic import BaseModel, HttpUrl

from backend.common.core.enums import CollectionMethod, SiteStatus
from backend.common.models.base_document import BaseDocument


class ScrapeMethodConfiguration(BaseModel):
    document_extensions: list[str]
    url_keywords: list[str]
    proxy_exclusions: list[PydanticObjectId] = []
    wait_for: list[str] = []
    wait_for_timeout_ms: int = 0
    search_in_frames: bool = False
    follow_links: bool = False
    follow_link_keywords: list[str]
    follow_link_url_keywords: list[str]


class UpdateScrapeMethodConfiguration(BaseModel):
    document_extensions: list[str] | None = None
    url_keywords: list[str] | None = None
    proxy_exclusions: list[PydanticObjectId] | None = None
    wait_for: list[str] | None = None
    follow_links: bool | None = None
    follow_link_keywords: list[str] | None = None
    follow_link_url_keywords: list[str] | None = None
    wait_for_timeout_ms: int = 0
    search_in_frames: bool = False


class BaseUrl(BaseModel):
    url: HttpUrl
    name: str = ""
    status: str = "ACTIVE"


class NewSite(BaseModel):
    name: str
    base_urls: list[BaseUrl] = []
    collection_method: str | None = CollectionMethod.Automated
    scrape_method: str | None = ""
    scrape_method_configuration: ScrapeMethodConfiguration | None = None
    tags: list[str] = []
    playbook: str | None = None
    cron: str | None = ""
    status: str | None = SiteStatus.NEW


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
    playbook: str | None = None
    status: str | None = None
    assignee: PydanticObjectId | None = None


class Site(BaseDocument, NewSite):
    disabled: bool
    last_run_status: str | None = None
    collection_method: str | None = CollectionMethod.Automated
    last_run_time: datetime | None = None
    assignee: PydanticObjectId | None = None


# Deprecated
class NoAssigneeSite(Site):
    assignee: PydanticObjectId | None = None

    class Collection:
        name = "Site"


class NoStatusSite(NoAssigneeSite):
    status: str | None = None

    class Collection:
        name = "Site"


class NoFollowLinkScrapeConfig(ScrapeMethodConfiguration):
    follow_links: bool | None = None
    follow_link_keywords: list[str] | None = None
    follow_link_url_keywords: list[str] | None = None


class NoFollowLinkSite(NoStatusSite):
    scrape_method_configuration: NoFollowLinkScrapeConfig

    class Collection:
        name = "Site"


class LastStatusSite(NoFollowLinkSite):
    last_status: str | None = None

    class Collection:
        name = "Site"


class NoScrapeConfigSite(LastStatusSite):
    scrape_method_configuration: NoFollowLinkScrapeConfig | None = None

    class Collection:
        name = "Site"


class SingleUrlSite(NoScrapeConfigSite):
    base_url: HttpUrl | None = None

    class Collection:
        name = "Site"

class CollectionTypeSite(SingleUrlSite):
    collection_type: str | None = CollectionMethod.Automated

    class Collection:
        name = "Site"




