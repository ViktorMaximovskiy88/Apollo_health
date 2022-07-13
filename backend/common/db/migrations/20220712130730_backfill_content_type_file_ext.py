import logging
from beanie import free_fall_migration
from backend.common.models.document import RetrievedDocument
from backend.scrapeworker.common.models import extension_to_mimetype_map


class Forward:
    @free_fall_migration(document_models=[RetrievedDocument])
    async def backfill_content_type_file_ext(self, session):

        # updating docx, xlsx (very few since rollout)
        for ext in ["xlsx", "docx"]:
            result = await RetrievedDocument.get_motor_collection().update_many(
                {"file_extension": ext, "content_type": None},
                {"$set": {"content_type": extension_to_mimetype_map[ext]}},
            )
            logging.info(
                f"updating {ext} -> acknowledged={result.acknowledged} matched_count={result.matched_count} modified_count={result.modified_count}"
            )

        # updating the rest... to be what code default was -> pdf
        result = await RetrievedDocument.get_motor_collection().update_many(
            {
                "file_extension": {"$in": [None, "pdf"]},
                "content_type": None,
            },
            {
                "$set": {
                    "file_extension": "pdf",
                    "content_type": extension_to_mimetype_map["pdf"],
                }
            },
        )

        logging.info(
            f"updating pdf -> acknowledged={result.acknowledged} matched_count={result.matched_count} modified_count={result.modified_count}"
        )


class Backward:
    @free_fall_migration(document_models=[RetrievedDocument])
    async def backfill_content_type_file_ext(self, session):
        logging.info("there is no undo here")
        pass
