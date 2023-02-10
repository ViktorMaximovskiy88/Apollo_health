from beanie import free_fall_migration

from backend.common.models.work_queue import WorkQueue


class Forward:
    @free_fall_migration(document_models=[WorkQueue])
    async def add_requires_comment_to_doc_and_payer_fam(self, session):
        await WorkQueue.get_motor_collection().update_many(
            {"submit_actions": {"$elemMatch": {"label": "Reject Classification"}}},
            {"$set": {"submit_actions.$[element].require_comment": True}},
            False,
            [{"element.label": "Reject Classification"}],
        )

        await WorkQueue.get_motor_collection().update_many(
            {"submit_actions": {"$elemMatch": {"label": "Reject Family"}}},
            {"$set": {"submit_actions.$[element].require_comment": True}},
            False,
            [{"element.label": "Reject Family"}],
        )


class Backward:
    @free_fall_migration(document_models=[WorkQueue])
    async def removes_requires_comment_to_doc_and_payer_fam(self, session):
        await WorkQueue.get_motor_collection().update_many(
            {"submit_actions": {"$elemMatch": {"label": "Reject Classification"}}},
            {"$unset": {"submit_actions.$[element].require_comment": ""}},
            False,
            [{"element.label": "Reject Classification"}],
        )

        await WorkQueue.get_motor_collection().update_many(
            {"submit_actions": {"$elemMatch": {"label": "Reject Family"}}},
            {"$unset": {"submit_actions.$[element].require_comment": ""}},
            False,
            [{"element.label": "Reject Family"}],
        )
