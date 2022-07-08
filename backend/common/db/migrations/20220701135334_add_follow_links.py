from beanie import iterative_migration
from backend.common.models.site import (
    NoFollowLinkSite,
    Site,
)


class Forward:
    @iterative_migration()
    async def add_follow_links(
        self,
        input_document: NoFollowLinkSite,
        output_document: Site,
    ):
        output_document.scrape_method_configuration.follow_links = False
        output_document.scrape_method_configuration.follow_link_keywords = []
        output_document.scrape_method_configuration.follow_link_url_keywords = []


class Backward:
    @iterative_migration()
    async def remove_follow_links(
        self,
        input_document: Site,
        output_document: NoFollowLinkSite,
    ):
        output_document.scrape_method_configuration.follow_links = None
        output_document.scrape_method_configuration.follow_link_keywords = None
        output_document.scrape_method_configuration.follow_link_url_keywords = None
