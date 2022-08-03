import logging

from beanie import free_fall_migration

from backend.common.models.document import RetrievedDocument


class Forward:
    @free_fall_migration(document_models=[RetrievedDocument])
    async def reset_existing_aliases(self, session):

        result = await RetrievedDocument.get_motor_collection().update_many(
            {},
            [{"$set": {"file_checksum_aliases": ["$checksum"]}}],
        )

        logging.info(
            f"updating file_checksum_aliases -> acknowledged={result.acknowledged} matched_count={result.matched_count} modified_count={result.modified_count}"  # noqa
        )


class Backward:
    @free_fall_migration(document_models=[RetrievedDocument])
    async def reset_existing_aliases(self, session):
        logging.info("there is no undo here, again")
        pass
