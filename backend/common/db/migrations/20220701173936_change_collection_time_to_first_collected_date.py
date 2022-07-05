from beanie import iterative_migration
from backend.common.models.document import (
    RetrievedDocument,
    CollectionTimeRetrievedDocument,
)


class Forward:
    @iterative_migration()
    async def change_collection_time_to_first_collected_date(
        self,
        input_document: CollectionTimeRetrievedDocument,
        output_document: RetrievedDocument,
    ):
        output_document.first_collected_date = input_document.collection_time


class Backward:
    @iterative_migration()
    async def change_first_collected_date_to_collection_time(
        self,
        input_document: RetrievedDocument,
        output_document: CollectionTimeRetrievedDocument,
    ):
        output_document.collection_time = input_document.first_collected_date
