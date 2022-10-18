from datetime import datetime
from xmlrpc.client import boolean

from beanie import PydanticObjectId
from pydantic import BaseModel, Field, HttpUrl

from backend.common.core.enums import CollectionMethod, SearchableType, SiteStatus
from backend.common.models.base_document import BaseDocument


class AttrSelector(BaseModel):
    attr_element: str | None = "a"
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
    document_extensions: list[str] = []
    url_keywords: list[str] = []
    proxy_exclusions: list[PydanticObjectId] = []
    wait_for: list[str] = []
    wait_for_timeout_ms: int = 500
    base_url_timeout_ms: int = 30000
    search_in_frames: bool = False
    follow_links: bool = False
    follow_link_keywords: list[str] = []
    follow_link_url_keywords: list[str] = []
    searchable: bool = False
    searchable_type: SearchableType | None = None
    searchable_input: AttrSelector | None = None
    searchable_submit: AttrSelector | None = None
    attr_selectors: list[AttrSelector] = []
    html_attr_selectors: list[AttrSelector] = []
    html_exclusion_selectors: list[AttrSelector] = []
    focus_therapy_configs: list[FocusTherapyConfig] = []
    allow_docdoc_updates: bool = False


class UpdateScrapeMethodConfiguration(BaseModel):
    document_extensions: list[str] | None = None
    url_keywords: list[str] | None = None
    proxy_exclusions: list[PydanticObjectId] | None = None
    wait_for: list[str] | None = None
    follow_links: bool | None = None
    follow_link_keywords: list[str] | None = None
    follow_link_url_keywords: list[str] | None = None
    searchable: bool | None = None
    searchable_type: SearchableType | None = None
    searchable_input: AttrSelector | None = None
    searchable_submit: AttrSelector | None = None
    wait_for_timeout_ms: int = 0
    search_in_frames: bool = False
    attr_selectors: list[AttrSelector] | None = None
    html_attr_selectors: list[AttrSelector] = []
    html_exclusion_selectors: list[AttrSelector] = []
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
    scrape_method_configuration: ScrapeMethodConfiguration = ScrapeMethodConfiguration()
    tags: list[str] = []
    playbook: str | None = None
    cron: str | None = ""
    status: str | None = SiteStatus.NEW
    doc_type_threshold_override: bool = False
    doc_type_threshold: float = 0.75
    lineage_threshold_override: bool = False
    lineage_threshold: float = 0.75


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
    doc_type_threshold_override: bool | None = None
    doc_type_threshold: float | None = None
    lineage_threshold_override: bool | None = None
    lineage_threshold: float | None = None


class UpdateSiteAssigne(BaseModel):
    id: PydanticObjectId = Field(alias="_id")


class Site(BaseDocument, NewSite):
    disabled: bool = False
    last_run_status: str | None = None
    collection_method: str | None = CollectionMethod.Automated
    collection_hold: datetime | None = None
    last_run_time: datetime | None = None
    assignee: PydanticObjectId | None = None
    is_running_manual_collection: boolean = False
    # Instead of always filtering out not_found on doc docs requiring an index,
    # only filter when a site has manually collected and selected NOT_FOUND.
    has_not_found_documents: boolean = False


# Deprecated
class NoSearchableHtmlConfig(ScrapeMethodConfiguration):
    searchable: bool | None = None
    html_attr_selectors: list[AttrSelector] | None = None
    html_exclusion_selectors: list[AttrSelector] | None = None


class NoSearchableHtmlSite(Site):
    scrape_method_configuration: NoSearchableHtmlConfig

    class Collection:
        name = "Site"


class NoDocDocUpdatesConfig(NoSearchableHtmlConfig):
    allow_docdoc_updates: bool | None = None


class NoDocDocUpdatesSite(NoSearchableHtmlSite):
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


class ActiveUrlResponse(BaseModel):
    in_use: bool
    site: Site | None = None
