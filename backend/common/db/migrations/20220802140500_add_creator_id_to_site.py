from beanie import iterative_migration

from backend.common.models.site import Site


class Forward:
    @iterative_migration()
    async def add_creator_id_to_site(self, input_document: Site, output_document: Site):
        if not input_document.creator_id:
            output_document.creator_id = None


class Backward:
    @iterative_migration()
    async def remove_creator_id_from_site(self, input_document: Site, output_document: Site):
        output_document.creator_id = None
