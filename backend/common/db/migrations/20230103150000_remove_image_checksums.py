import logging

from beanie import free_fall_migration

from backend.common.models.doc_document import DocDocument


class Forward:
    @free_fall_migration(document_models=[DocDocument])
    async def remove_image_checksums(self, session):
        result = await DocDocument.get_motor_collection().update_many(
            {"image_checksums": {"$exists": True}}, {"$unset": {"image_checksums": ""}}
        )
        logging.info(
            f"removing image_checksums records -> acknowledged={result.acknowledged} matched_count={result.matched_count} modified_count={result.modified_count}"  # noqa
        )

        result = await DocDocument.get_motor_collection().update_many(
            {"content_checksum": {"$exists": True}}, {"$unset": {"content_checksum": ""}}
        )
        logging.info(
            f"removing image_checksums records -> acknowledged={result.acknowledged} matched_count={result.matched_count} modified_count={result.modified_count}"  # noqa
        )


class Backward:
    ...
