import logging

from beanie import free_fall_migration

from backend.common.models.site import Site


class Forward:
    @free_fall_migration(document_models=[Site])
    async def set_allow_docdoc_updates_to_true(self, session):
        result = await Site.get_motor_collection().update_many(
            {},
            [{"$set": {"scrape_method_configuration.allow_docdoc_updates": True}}],
        )
        logging.info(
            f"set Site.scrape_method_configuration.allow_docdoc_updates to True  -> acknowledged={result.acknowledged} matched_count={result.matched_count} modified_count={result.modified_count}"  # noqa
        )


class Backward:
    pass
