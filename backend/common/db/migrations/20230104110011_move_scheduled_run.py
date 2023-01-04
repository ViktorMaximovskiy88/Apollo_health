from beanie import free_fall_migration

from backend.common.models.site import Site


class Forward:
    @free_fall_migration(document_models=[Site])
    async def update_tags(self, session):
        await Site.find({"cron": "0 12 * * *"}).update_many({"$set": {"cron": "0 8 * * *"}})
        await Site.find({"cron": "0 12 * * 0"}).update_many({"$set": {"cron": "0 8 * * 0"}})
        await Site.find({"cron": "0 12 1 * *"}).update_many({"$set": {"cron": "0 8 1 * *"}})


class Backward:
    ...
