from datetime import datetime

from beanie import PydanticObjectId
from pydantic import BaseModel, Field, HttpUrl

from backend.common.core.enums import CollectionMethod, SiteStatus
from backend.common.models.base_document import BaseDocument


class AttrSelector(BaseModel):
    attr_name: str
    attr_value: str | None = None
    has_text: str | None = None
    resource_address: bool = False


class FocusTherapyConfig(BaseModel):
    doc_type: str
    start_separator: str | None = None
    end_separator: str | None = None
    all_focus: bool = False


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
    attr_selectors: list[AttrSelector] = []
    focus_therapy_configs: list[FocusTherapyConfig] = []
    allow_docdoc_updates: bool = True


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
    attr_selectors: list[AttrSelector] | None = None
    focus_therapy_configs: list[FocusTherapyConfig] | None = None
    allow_docdoc_updates: bool | None = None


class BaseUrl(BaseModel):
    url: HttpUrl
    name: str = ""
    status: str = "ACTIVE"


class NewSite(BaseModel):
    creator_id: PydanticObjectId | None = None
    name: str
    base_urls: list[BaseUrl] = []
    collection_method: str | None = CollectionMethod.Automated
    scrape_method: str | None = ""
    scrape_method_configuration: ScrapeMethodConfiguration
    tags: list[str] = []
    playbook: str | None = None
    cron: str | None = ""
    status: str | None = SiteStatus.NEW


class UpdateSite(BaseModel):
    name: str | None = None
    base_urls: list[BaseUrl] | None = None
    scrape_method: str | None = None
    collection_method: str | None = None
    collection_hold: datetime | None = None
    tags: list[str] | None = None
    cron: str | None = None
    disabled: bool | None = None
    last_run_time: datetime | None = None
    scrape_method_configuration: UpdateScrapeMethodConfiguration | None = None
    playbook: str | None = None
    status: str | None = None
    assignee: PydanticObjectId | None = None


class UpdateSiteAssigne(BaseModel):
    id: PydanticObjectId = Field(alias="_id")


class Site(BaseDocument, NewSite):
    disabled: bool
    last_run_status: str | None = None
    collection_method: str | None = CollectionMethod.Automated
    collection_hold: datetime | None = None
    last_run_time: datetime | None = None
    assignee: PydanticObjectId | None = None


# Deprecated
class NoDocDocUpdatesConfig(ScrapeMethodConfiguration):
    allow_docdoc_updates: bool | None = None


class NoDocDocUpdatesSite(Site):
    scrape_method_configuration: NoDocDocUpdatesConfig

    class Collection:
        name = "Site"


class NoFocusConfigsScrapeConfig(ScrapeMethodConfiguration):
    focus_therapy_configs: list[FocusTherapyConfig] | None = None


class NoFocusConfigsSite(NoDocDocUpdatesSite):
    scrape_method_configuration: NoFocusConfigsScrapeConfig

    class Collection:
        name = "Site"


class NoAttrSelectorsScrapeConfig(ScrapeMethodConfiguration):
    attr_selectors: list[AttrSelector] | None = None


class NoAttrSelectorSite(NoFocusConfigsSite):
    scrape_method_configuration: NoAttrSelectorsScrapeConfig

    class Collection:
        name = "Site"


class NoAssigneeSite(NoAttrSelectorSite):
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
