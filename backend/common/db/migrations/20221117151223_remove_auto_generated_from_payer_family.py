from beanie import free_fall_migration

from backend.common.models.payer_family import PayerFamily


class Forward:
    @free_fall_migration(document_models=[PayerFamily])
    async def remove_doc_type_from_Payer_Family(self, session):
        await PayerFamily.get_motor_collection().update_many(
            {},
            {
                "$unset": {"auto_generated": ""},
            },
        )


class Backward:
    @free_fall_migration(document_models=[PayerFamily])
    async def put_doc_type_on_Payer_Family(self, session):
        await PayerFamily.get_motor_collection().update_many(
            {},
            {
                "$set": {"auto_generated": False},
            },
        )
