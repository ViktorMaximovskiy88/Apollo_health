from beanie import free_fall_migration

from backend.common.models.app_config import AppConfig


class Forward:
    @free_fall_migration(document_models=[AppConfig])
    async def add_default_config(self, session):
        initial_config = AppConfig(key="collections", data={"defaultLastNDays": 10})
        await initial_config.create()


class Backward:
    @free_fall_migration(document_models=[AppConfig])
    async def delete_default_config(self, session):
        await AppConfig.find({}).delete
