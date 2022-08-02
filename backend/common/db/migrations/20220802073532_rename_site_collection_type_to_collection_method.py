from beanie import iterative_migration
from backend.common.models.site import (
    Site
)


class Forward:
    @iterative_migration()
    async def change_site_collection_type_to_collection_method(
        self,
        input_document: Site,
        output_document: Site,
    ):
        output_document.collection_type = input_document.collection_method


class Backward:
    @iterative_migration()
    async def change_site_collection_method_to_collection_type(
        self,
        input_document: Site,
        output_document: Site,
    ):
        output_document.collection_method = input_document.collection_type
