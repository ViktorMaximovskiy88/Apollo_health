from beanie import free_fall_migration

from backend.common.core.enums import ApprovalStatus
from backend.common.models.doc_document import DocDocument


class Forward:
    @free_fall_migration(document_models=[DocDocument])
    async def change_classification_status_from_pending_to_queued(self, session):
        DocDocument.get_motor_collection().update_many(
            {"classification_status": ApprovalStatus.PENDING},
            {"$set": {"classification_status": ApprovalStatus.QUEUED}},
        )


class Backward:
    ...
