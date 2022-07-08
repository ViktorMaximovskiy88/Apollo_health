from beanie import iterative_migration
from backend.common.models.site import Site
from backend.common.core.enums import TaskStatus, SiteStatus


class Forward:
    @iterative_migration()
    async def add_status_to_site(self, input_document: Site, output_document: Site):
        if output_document.status:
            return
        if input_document.last_run_status == TaskStatus.FAILED:
            output_document.status = SiteStatus.QUALITY_HOLD
        else:
            output_document.status = SiteStatus.NEW


class Backward:
    @iterative_migration()
    async def remove_status_from_site(
        self, input_document: Site, output_document: Site
    ):
        output_document.status = None
