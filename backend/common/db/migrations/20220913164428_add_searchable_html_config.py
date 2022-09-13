from beanie import iterative_migration

from backend.common.models.site import NoSearchableHtmlSite, Site


class Forward:
    @iterative_migration()
    async def add_searchable_and_html_configs(
        self, input_document: NoSearchableHtmlSite, output_document: Site
    ):
        output_document.scrape_method_configuration.searchable = False
        output_document.scrape_method_configuration.html_attr_selectors = []
        output_document.scrape_method_configuration.html_exclusion_selectors = []


class Backward:
    @iterative_migration()
    async def remove_searchable_and_html_configs(
        self, input_document: Site, output_document: NoSearchableHtmlSite
    ):
        output_document.scrape_method_configuration.searchable = None
        output_document.scrape_method_configuration.html_attr_selectors = None
        output_document.scrape_method_configuration.html_exclusion_selectors = None
