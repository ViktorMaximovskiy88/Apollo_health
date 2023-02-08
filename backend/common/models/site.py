from datetime import datetime

from beanie import PydanticObjectId
from pydantic import Field, HttpUrl

from backend.common.core.enums import (
    CmsDocType,
    CollectionMethod,
    ScrapeMethod,
    SearchableType,
    SectionType,
    SiteStatus,
)
from backend.common.models.base_document import BaseDocument, BaseModel
from backend.common.models.pipeline import SitePipelineStages


class AttrSelector(BaseModel):
    attr_element: str | None = "a"
    attr_name: str
    attr_value: str | None = None
    has_text: str | None = None
    resource_address: bool = False


class FocusSectionConfig(BaseModel):
    doc_type: str
    section_type: list[SectionType]
    start_separator: str | None = None
    end_separator: str | None = None
    all_focus: bool = False

    def __hash__(self):
        config = self.__dict__
        config["section_type"] = tuple(config["section_type"])
        return hash(tuple(config.values()))


class ScrapeMethodConfiguration(BaseModel):
    document_extensions: list[str] = []
    url_keywords: list[str] = []
    proxy_exclusions: list[PydanticObjectId] = []
    wait_for: list[str] = []
    wait_for_timeout_ms: int = 500
    base_url_timeout_ms: int = 30000
    search_in_frames: bool = False
    attr_selectors: list[AttrSelector] = []
    html_attr_selectors: list[AttrSelector] = []
    html_exclusion_selectors: list[AttrSelector] = []
    focus_section_configs: list[FocusSectionConfig] = []
    allow_docdoc_updates: bool = False
    cms_doc_types: list[CmsDocType] = []
    debug: bool = False

    # Follow Links
    follow_links: bool = False
    follow_link_keywords: list[str] = []
    follow_link_url_keywords: list[str] = []
    # if Falsey and follow_links True, only scrape pages found by follow links
    scrape_base_page: bool | None = None

    # Searchables
    searchable: bool = False
    search_prefix_length: int | None = None
    searchable_playbook: str | None = None
    searchable_type: list[SearchableType] = []
    searchable_input: AttrSelector | None = None
    searchable_submit: AttrSelector | None = None


class UpdateScrapeMethodConfiguration(BaseModel):
    document_extensions: list[str] | None = None
    url_keywords: list[str] | None = None
    proxy_exclusions: list[PydanticObjectId] | None = None
    wait_for: list[str] | None = None
    follow_links: bool | None = None
    follow_link_keywords: list[str] | None = None
    follow_link_url_keywords: list[str] | None = None
    scrape_base_page: bool | None = None
    searchable: bool | None = None
    search_prefix_length: int | None = None
    searchable_playbook: str | None = None
    searchable_type: list[SearchableType] = []
    searchable_input: AttrSelector | None = None
    searchable_submit: AttrSelector | None = None
    wait_for_timeout_ms: int = 0
    search_in_frames: bool = False
    attr_selectors: list[AttrSelector] | None = None
    html_attr_selectors: list[AttrSelector] = []
    html_exclusion_selectors: list[AttrSelector] = []
    focus_section_configs: list[FocusSectionConfig] | None = None
    allow_docdoc_updates: bool | None = None
    cms_doc_types: list[CmsDocType] = []
    debug: bool = False


class BaseUrl(BaseModel):
    url: HttpUrl
    name: str = ""
    status: str = "ACTIVE"


class NewSite(BaseModel):
    creator_id: PydanticObjectId | None = None
    name: str
    base_urls: list[BaseUrl] = []
    collection_method: str | None = CollectionMethod.Automated
    scrape_method: ScrapeMethod | None = ScrapeMethod.Simple
    scrape_method_configuration: ScrapeMethodConfiguration = ScrapeMethodConfiguration()
    tags: list[str] = []
    playbook: str | None = None
    cron: str | None = ""
    status: str | None = SiteStatus.NEW
    doc_type_threshold_override: bool = False
    doc_type_threshold: float = 0.75
    lineage_threshold_override: bool = False
    lineage_threshold: float = 0.75
    payer_work_instructions: str | None = None


class UpdateSite(BaseModel):
    name: str | None = None
    base_urls: list[BaseUrl] | None = None
    scrape_method: ScrapeMethod | None = None
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
    last_run_documents: int | None = None
    payer_work_instructions: str | None = None


class UpdateSiteAssigne(BaseModel):
    id: PydanticObjectId = Field(alias="_id")


class Site(BaseDocument, NewSite):
    disabled: bool = False
    last_run_status: str | None = None
    collection_method: str | None = CollectionMethod.Automated
    collection_hold: datetime | None = None
    last_run_time: datetime | None = None
    assignee: PydanticObjectId | None = None
    last_run_documents: int | None = None
    pipeline_stages: SitePipelineStages | None = None

    @classmethod
    async def get_active_sites(cls):
        return await Site.find({"disabled": False})


# Deprecated
class FocusTherapyConfig(BaseModel):
    doc_type: str
    start_separator: str | None = None
    end_separator: str | None = None
    all_focus: bool = False


class NoFocusTagConfig(ScrapeMethodConfiguration):
    focus_section_configs: list[FocusSectionConfig] | None = None
    focus_therapy_configs: list[FocusTherapyConfig]


class NoFocusTagConfigSite(Site):
    scrape_method_configuration: NoFocusTagConfig

    class Colleciton:
        name = "Site"


class NoSearchableHtmlConfig(NoFocusTagConfig):
    searchable: bool | None = None
    html_attr_selectors: list[AttrSelector] | None = None
    html_exclusion_selectors: list[AttrSelector] | None = None


class NoSearchableHtmlSite(NoFocusTagConfigSite):
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
