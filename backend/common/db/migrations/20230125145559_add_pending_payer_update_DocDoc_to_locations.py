from beanie import free_fall_migration

from backend.common.models.doc_document import DocDocument


class Forward:
    @free_fall_migration(document_models=[DocDocument])
    async def add_pending_payer_update_to_DocDoc_location(self, session):
        await DocDocument.get_motor_collection().update_many(
            {},
            {"$set": {"locations.$[].pending_payer_update": False}},
        )


class Backward:
    @free_fall_migration(document_models=[DocDocument])
    async def remove_pending_payer_update_to_DocDoc_location(self, session):
        await DocDocument.get_motor_collection().update_many(
            {},
            {"$unset": {"locations.$[].pending_payer_update": ""}},
        )
