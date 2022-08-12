from beanie import iterative_migration

from backend.common.models.site import NoAttrSelectorSite, Site


class Forward:
    @iterative_migration
    async def add_attr_selectors(
        self,
        input_document: NoAttrSelectorSite,
        output_document: Site,
    ):
        output_document.scrape_method_configuration.attr_selectors = []


class Backward:
    @iterative_migration
    async def remove_attr_selectors(
        self,
        input_document: Site,
        output_document: NoAttrSelectorSite,
    ):
        output_document.scrape_method_configuration.attr_selectors = None
