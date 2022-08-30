from beanie import free_fall_migration, iterative_migration

from backend.common.models.site import NoDocDocUpdatesSite, Site


class Forward:
    @iterative_migration()
    async def add_allow_docdoc_updates(
        self,
        input_document: NoDocDocUpdatesSite,
        output_document: Site,
    ):
        output_document.scrape_method_configuration.allow_docdoc_updates = True


class Backward:
    @free_fall_migration(document_models=[Site])
    async def remove_allow_docdoc_updates(self, session):
        await Site.get_motor_collection().update_many(
            {},
            {
                "$unset": {"scrape_method_configuration.allow_docdoc_updates": ""},
            },
        )
