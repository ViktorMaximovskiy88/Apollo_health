from beanie import free_fall_migration

from backend.common.models.work_queue import WorkQueue


class Forward:
    @free_fall_migration(document_models=[WorkQueue])
    async def update_work_queues(self, session):
        await WorkQueue.get_motor_collection().update_many(
            {"name": {"$in": ["Document & Payer Family", "Document & Payer Family Hold"]}},
            {
                "$push": {
                    "submit_actions": {
                        "label": "Reject Classification",
                        "submit_action": {
                            "classification_status": "HOLD",
                            "family_status": "PENDING",
                        },
                        "primary": True,
                    }
                }
            },
        )

        await WorkQueue.get_motor_collection().update_many(
            {"name": {"$in": ["Translation Config", "Translation Config Hold"]}},
            {
                "$push": {
                    "submit_actions": [
                        {
                            "label": "Reject Classification",
                            "submit_action": {
                                "classification_status": "HOLD",
                                "family_status": "PENDING",
                            },
                            "primary": True,
                        },
                        {
                            "label": "Reject Family",
                            "submit_action": {
                                "family_status": "HOLD",
                                "content_extraction_status": "PENDING",
                            },
                            "primary": True,
                        },
                    ],
                }
            },
        )


class Backward:
    ...
