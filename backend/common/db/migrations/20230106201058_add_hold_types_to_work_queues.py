from beanie import free_fall_migration

from backend.common.models.work_queue import WorkQueue


class Forward:
    @free_fall_migration(document_models=[WorkQueue])
    async def add_hold_types(self, session):
        await WorkQueue.find_one({"name": "Classification"}).update_one(
            {
                "$set": {
                    "submit_actions.0.hold_types": [
                        "Source Hub Issue",
                        "Focus Tagging",
                        "Medical Codes (J/CPT)",
                        "Spanish / Other Language",
                    ]
                }
            }
        )
        await WorkQueue.find_one({"name": "Document & Payer Family"}).update_one(
            {"$set": {"submit_actions.0.hold_types": ["Source Hub Issue", "Backbone Issue"]}}
        )


class Backward:
    ...
