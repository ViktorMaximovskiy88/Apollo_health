from beanie import free_fall_migration

from backend.common.models.doc_document import DocDocument
from backend.common.models.document_family import DocumentFamily


class Forward:
    @free_fall_migration(document_models=[DocDocument, DocumentFamily])
    async def move_docfamily_to_doc_and_payer_to_doclocation(self, session):
        await DocDocument.get_motor_collection().update_many(
            {
                "locations": [
                    {"$exists": True},
                    {
                        "$elemMatch": {
                            "document_family_id": {"$exists": True},
                        }
                    },
                ]
            },
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
    @free_fall_migration(document_models=[DocDocument, DocumentFamily])
    async def move_docfamily_to_doc_and_payer_to_doclocation(self, session):
        await DocDocument.get_motor_collection().update_many(
            {
                "locations": [
                    {"$exists": True},
                    {
                        "$elemMatch": {
                            "payer_family_id": {"$exists": True},
                        }
                    },
                ],
            },
            [
                {
                    "$set": {"locations.$[].document_family_id": None},
                },
                {"$unset": {"locations.$[].payer_family_id": ""}},
            ],
        )

        await DocumentFamily.get_motor_collection().update_many(
            {"payer_info": {"$exists": False}},
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
