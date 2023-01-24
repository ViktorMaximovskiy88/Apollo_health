from beanie import free_fall_migration

from backend.common.models.site import Site


class Forward:
    @free_fall_migration(document_models=[Site])
    async def add_cms_doc_type(self, session):
        await Site.get_motor_collection().update_many(
            {"scrape_method_configuration.cms_doc_types": {"$exists": False}},
            {"$set": {"scrape_method_configuration.cms_doc_types": []}},
        )


class Backward:
    ...
