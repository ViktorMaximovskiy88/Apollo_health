import logging

from beanie import free_fall_migration

from backend.common.models.doc_document import DocDocument
from backend.common.models.document import RetrievedDocument


class Forward:
    @free_fall_migration(document_models=[DocDocument, RetrievedDocument])
    async def doc_doc_file_ext(self, session):
        result = await DocDocument.get_motor_collection().update_many(
            {"file_extension": None},
            {"$set": {"file_extension": "pdf"}},
        )

        logging.info(
            f"updating pdfs -> acknowledged={result.acknowledged} matched_count={result.matched_count} modified_count={result.modified_count}"  # noqa
        )


class Backward:
    @free_fall_migration(document_models=[DocDocument])
    async def doc_doc_file_ext(self, session):
        pass
