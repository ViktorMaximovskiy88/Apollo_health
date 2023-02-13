from beanie import free_fall_migration

from backend.app.scripts.create_work_queues import execute
from backend.common.models.work_queue import WorkQueue


class Forward:
    @free_fall_migration(document_models=[WorkQueue])
    async def update_work_queue(self, session):
        await execute()


class Backend:
    ...
