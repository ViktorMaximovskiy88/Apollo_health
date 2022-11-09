from beanie import free_fall_migration

from backend.common.models.site import Site


class Forward:
    @free_fall_migration(document_models=[Site])
    async def update_tags(self, session):
        await Site.find({"cron": "0 16 * * *"}).update_many({"$set": {"cron": "0 12 * * *"}})
        await Site.find({"cron": "0 16 * * 0"}).update_many({"$set": {"cron": "0 12 * * 0"}})
        await Site.find({"cron": "0 16 1 * *"}).update_many({"$set": {"cron": "0 12 1 * *"}})


class Backward:
    ...
