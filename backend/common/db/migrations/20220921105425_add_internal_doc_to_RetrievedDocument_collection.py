from beanie import free_fall_migration

from backend.common.models import RetrievedDocument


class Forward:
    @free_fall_migration(document_models=[RetrievedDocument])
    async def add_internal_document_field(self, session):
        await RetrievedDocument.get_motor_collection().update_many(
            {}, {"$set": {"internal_document": False}}
        )


class Backward:
    @free_fall_migration(document_models=[RetrievedDocument])
    async def remove_internal_document_field(self, session):
        await RetrievedDocument.get_motor_collection().update_many(
            {}, {"$unset": {"internal_document": ""}}
        )
