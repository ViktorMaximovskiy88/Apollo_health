import logging

from beanie import free_fall_migration

from backend.common.models.work_queue import WorkQueue


class Forward:
    @free_fall_migration(document_models=[WorkQueue])
    async def update_grace_period(self, session):
        result = await WorkQueue.find_all().update({"$set": {"grace_period": 30}})

        logging.info(
            f"WorkQueue -> acknowledged={result.acknowledged} modified_count={result.modified_count}"  # noqa
        )


class Backward:
    ...
