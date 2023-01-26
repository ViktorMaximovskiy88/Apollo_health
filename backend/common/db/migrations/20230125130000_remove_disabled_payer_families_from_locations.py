import logging

from beanie import free_fall_migration

from backend.common.core.enums import ApprovalStatus
from backend.common.models.doc_document import DocDocument
from backend.common.models.payer_family import PayerFamily
from backend.common.models.work_queue import WorkQueue


class Forward:
    @free_fall_migration(document_models=[WorkQueue])
    async def remove_disabled_payer_families_from_locations(self, session):
        disabled_pfs = await PayerFamily.find_many({"disabled": True}).to_list()

        result = await DocDocument.get_motor_collection().update_many(
            {"locations.payer_family_id": {"$in": [pf.id for pf in disabled_pfs]}},
            {
                "$set": {
                    "locations.$.payer_family_id": None,
                    "family_status": ApprovalStatus.QUEUED.value,
                    "status": ApprovalStatus.PENDING.value,
                }
            },
        )
        logging.info(
            f"removing disabled payer families from Doc Document locations -> acknowledged={result.acknowledged} matched_count={result.matched_count} modified_count={result.modified_count}"  # noqa
        )


class Backward:
    ...
