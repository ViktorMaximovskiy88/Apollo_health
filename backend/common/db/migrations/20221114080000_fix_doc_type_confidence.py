import logging

from beanie import free_fall_migration

from backend.common.models.doc_document import DocDocument
from backend.common.models.document import RetrievedDocument


async def update_doc_type_confidence(from_value: int, to_value: float):

    result = await RetrievedDocument.get_motor_collection().update_many(
        {"doc_type_confidence": from_value},
        {"$set": {"doc_type_confidence": to_value}},
    )
    logging.info(
        f"updating RetrievedDocument doc type from  {from_value} to {to_value} -> acknowledged={result.acknowledged} matched_count={result.matched_count} modified_count={result.modified_count}"  # noqa
    )

    result = await DocDocument.get_motor_collection().update_many(
        {"doc_type_confidence": from_value},
        {"$set": {"doc_type_confidence": to_value}},
    )
    logging.info(
        f"updating DocDocument doc type from  {from_value} to {to_value} -> acknowledged={result.acknowledged} matched_count={result.matched_count} modified_count={result.modified_count}"  # noqa
    )


class Forward:
    @free_fall_migration(document_models=[RetrievedDocument, DocDocument])
    async def fix_doc_type_confidence(self, session):
        await update_doc_type_confidence(100, 1)
        await update_doc_type_confidence(80, 0.8)
        await update_doc_type_confidence(70, 0.7)


class Backward:
    ...
