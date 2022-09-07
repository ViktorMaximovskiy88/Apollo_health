from beanie import free_fall_migration

from backend.common.models.config import Config


class Forward:
    @free_fall_migration(document_models=[Config])
    async def add_default_config(self, session):
        initial_config = Config(key="collections", data={"defaultLastNDays": 10})
        await initial_config.create()


class Backward:
    @free_fall_migration(document_models=[Config])
    async def delete_default_config(self, session):
        await Config.find({}).delete
