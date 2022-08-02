from beanie import iterative_migration
from backend.common.models.site import (
    Site,
    CollectionTypeSite
)

class Forward:
    @iterative_migration()
    async def change_site_collection_type_to_collection_method(
        self,
        input_document: Site,
        output_document: CollectionTypeSite,
    ):
        if output_document.collection_method:
            return

        output_document.collection_method = input_document.collection_type

        if output_document.collection_type:
            output_document.collection_type = None;


class Backward:
    @iterative_migration()
    async def change_site_collection_method_to_collection_type(
        self,
        input_document: CollectionTypeSite,
        output_document: Site,
    ):
        if output_document.collection_type:
            return

        output_document.collection_type = input_document.collection_method
            
        if output_document.collection_method:
            output_document.collection_method = None;
