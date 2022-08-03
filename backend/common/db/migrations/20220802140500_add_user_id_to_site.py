from beanie import iterative_migration

from backend.common.models.site import Site


class Forward:
    @iterative_migration()
    async def add_user_id_to_site(self, input_document: Site, output_document: Site):
        if not input_document.user_id:
            output_document.user_id = None


class Backward:
    @iterative_migration()
    async def remove_user_id_from_site(self, input_document: Site, output_document: Site):
        output_document.user_id = None
