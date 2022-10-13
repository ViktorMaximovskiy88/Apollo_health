from beanie import free_fall_migration

from backend.common.models.doc_document import DocDocument
from backend.common.models.document_family import DocumentFamily


class Forward:
    ...

    @free_fall_migration(document_models=[DocDocument, DocumentFamily])
    async def replace_doc_fam_field_with_payer_fam_DocDoc_Location_remove_payer_info_on_doc_family(
        self, session
    ):
        await DocDocument.get_motor_collection().update_many(
            {"locations": {"$exists": True}},
            {
                "$set": {"locations.$[].payer_family_id": None},
                "$unset": {"locations.$[].document_family_id": ""},
            },
        )

        await DocumentFamily.get_motor_collection().update_many(
            {"payer_info": {"$exists": True}},
            {
                "$unset": {"payer_info": ""},
            },
        )


class Backward:
    ...

    @free_fall_migration(document_models=[DocDocument, DocumentFamily])
    async def replace_payer_fam_field_with_doc_fam_on_DocDoc_Location_set_payer_info_on_doc_family(
        self, session
    ):
        await DocDocument.get_motor_collection().update_many(
            {"locations": {"$exists": True}},
            [
                {
                    "$set": {"locations.$[].document_family_id": None},
                },
                {"$unset": {"locations.$[].payer_family_id": ""}},
            ],
        )

        await DocumentFamily.get_motor_collection().update_many(
            {"payer_info": {"$exists": True}},
            [
                {
                    "$set": {
                        "payer_info": {
                            "payer_type": None,
                            "payer_ids": [],
                            "channels": [],
                            "benefits": [],
                            "plan_types": [],
                            "regions": [],
                        }
                    },
                }
            ],
        )
