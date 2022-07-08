from beanie import iterative_migration
from backend.common.models.document import (
    LastSeenRetrievedDocument,
    CollectionTimeRetrievedDocument,
)


class Forward:
    @iterative_migration()
    async def change_last_seen_to_last_collected_date(
        self,
        input_document: LastSeenRetrievedDocument,
        output_document: CollectionTimeRetrievedDocument,
    ):
        output_document.last_collected_date = input_document.last_seen


class Backward:
    @iterative_migration()
    async def change_last_collected_date_to_last_seen(
        self,
        input_document: CollectionTimeRetrievedDocument,
        output_document: LastSeenRetrievedDocument,
    ):
        output_document.last_seen = input_document.last_collected_date
