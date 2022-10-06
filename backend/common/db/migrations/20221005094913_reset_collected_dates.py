import logging

from beanie import free_fall_migration

from backend.common.models.doc_document import DocDocument
from backend.common.models.document import RetrievedDocument


class Forward:
    @free_fall_migration(document_models=[DocDocument])
    async def set_final_effective_date(self, session):
        result = await RetrievedDocument.get_motor_collection().update_many(
            {"first_collected_date": {"$exists": False}},
            {"$set": {"first_collected_date": {"$min": "$locations.first_collected_date"}}},
        )
        logging.info(
            f"reset retrieved document first_collected_date -> acknowledged={result.acknowledged} matched_count={result.matched_count} modified_count={result.modified_count}"  # noqa
        )
        result = await RetrievedDocument.get_motor_collection().update_many(
            {"last_collected_date": {"$exists": False}},
            {"$set": {"last_collected_date": {"$max": "$locations.last_collected_date"}}},
        )
        logging.info(
            f"reset retrieved document last_collected_date -> acknowledged={result.acknowledged} matched_count={result.matched_count} modified_count={result.modified_count}"  # noqa
        )

        result = await DocDocument.get_motor_collection().update_many(
            {"first_collected_date": {"$exists": False}},
            [{"$set": {"first_collected_date": {"$min": "$locations.first_collected_date"}}}],
        )
        logging.info(
            f"reset doc document first_collected_date -> acknowledged={result.acknowledged} matched_count={result.matched_count} modified_count={result.modified_count}"  # noqa
        )
        result = await DocDocument.get_motor_collection().update_many(
            {"last_collected_date": {"$exists": False}},
            [{"$set": {"last_collected_date": {"$max": "$locations.last_collected_date"}}}],
        )
        logging.info(
            f"reset doc document last_collected_date -> acknowledged={result.acknowledged} matched_count={result.matched_count} modified_count={result.modified_count}"  # noqa
        )

        result = await DocDocument.get_motor_collection().update_many(
            {"final_effective_date": {"$exists": False}},
            [
                {
                    "$set": {
                        "final_effective_date": {
                            "$ifNull": [
                                "$final_effective_date",
                                {
                                    "$max": [
                                        "$effective_date",
                                        "$last_reviewed_date",
                                        "$last_updated_date",
                                    ]
                                },
                                "$first_collected_date",
                            ]
                        }
                    }
                }
            ],
        )
        logging.info(
            f"reset final_effective_date  -> acknowledged={result.acknowledged} matched_count={result.matched_count} modified_count={result.modified_count}"  # noqa
        )


class Backward:
    @free_fall_migration(document_models=[DocDocument, RetrievedDocument])
    async def add_locations(self, session):
        pass
