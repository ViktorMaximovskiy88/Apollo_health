from beanie import iterative_migration

from backend.common.models.site import LastStatusSite, Site


class Forward:
    @iterative_migration()
    async def change_last_status_to_last_run_status(
        self, input_document: LastStatusSite, output_document: Site
    ):
        if output_document.last_run_status:
            return
        output_document.last_run_status = input_document.last_status


class Backward:
    @iterative_migration()
    async def change_last_run_status_to_last_status(
        self, input_document: Site, output_document: LastStatusSite
    ):
        if output_document.last_status:
            return
        output_document.last_status = input_document.last_run_status
