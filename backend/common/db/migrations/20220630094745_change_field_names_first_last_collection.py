from beanie import iterative_migration
from backend.common.models.document import RetrievedDocument, OldRetrievedDocument


class Forward:
    @iterative_migration()
    async def change_first_last_collected_date(
            self, input_document: OldRetrievedDocument, output_document: RetrievedDocument
    ):
        output_document.first_collected_date = input_document.collection_time
        output_document.last_collected_date = input_document.last_seen


class Backward:
    @iterative_migration()
    async def change_collection_time_last_seen(
        self, input_document: RetrievedDocument, output_document: OldRetrievedDocument, 
    ):
        output_document.collection_time = input_document.first_collected_date
        output_document.last_seen = input_document.last_collected_date
