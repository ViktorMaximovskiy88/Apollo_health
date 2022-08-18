from beanie import iterative_migration

from backend.common.models.site import NoFocusConfigsSite, Site


class Forward:
    @iterative_migration
    async def add_focus_therapy_configs(
        self,
        input_document: NoFocusConfigsSite,
        output_document: Site,
    ):
        output_document.scrape_method_configuration.focus_therapy_configs = []


class Backward:
    @iterative_migration
    async def remove_focus_therapy_configs(
        self,
        input_document: Site,
        output_document: NoFocusConfigsSite,
    ):
        output_document.scrape_method_configuration.focus_therapy_configs = None
