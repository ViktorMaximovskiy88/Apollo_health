from beanie import iterative_migration

from backend.common.models.site import NoAssigneeSite, Site


class Forward:
    @iterative_migration()
    async def add_status_to_site(self, input_document: NoAssigneeSite, output_document: Site):
        if input_document.assignee:
            output_document.assignee = input_document.assignee
        else:
            output_document.assignee = None


class Backward:
    @iterative_migration()
    async def remove_status_from_site(self, input_document: Site, output_document: NoAssigneeSite):
        output_document.assignee = input_document.assignee
