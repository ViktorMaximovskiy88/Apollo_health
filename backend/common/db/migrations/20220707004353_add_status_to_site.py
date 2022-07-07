from beanie import iterative_migration
from backend.common.models.site import Site
from backend.common.core.enums import ScrapeTaskStatus, SiteStatus


class Forward:
    @iterative_migration()
    async def add_status_to_site(self, input_document: Site, output_document: Site):
        if input_document.last_run_status == ScrapeTaskStatus.FAILED:
            output_document.status = SiteStatus.QUALITY_HOLD
        else:
            output_document.status = SiteStatus.ONLINE


class Backward:
    @iterative_migration()
    async def remove_status_from_site(
        self, input_document: Site, output_document: Site
    ):
        output_document.status = None
