import logging

from beanie import free_fall_migration

from backend.common.models.doc_document import DocDocument
from backend.common.models.document import RetrievedDocument


class Forward:
    @free_fall_migration(document_models=[DocDocument])
    async def set_final_effective_date(self, session):
        result = await DocDocument.get_motor_collection().update_many(
            {},
            [
                {
                    "$set": {
                        "final_effective_date": {
                            "$ifNull": [
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
