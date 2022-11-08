import logging

from beanie import free_fall_migration

from backend.common.models.doc_document import DocDocument
from backend.common.models.document import RetrievedDocument


# there were 2 :p
async def update_doc_type(from_doc_type: str, to_doc_type: str):
    result = await DocDocument.get_motor_collection().update_many(
        {"document_type": from_doc_type},
        {"$set": {"document_type": to_doc_type}},
    )
    logging.info(
        f"updating docdoc doc type from  {from_doc_type} to {to_doc_type} -> acknowledged={result.acknowledged} matched_count={result.matched_count} modified_count={result.modified_count}"  # noqa
    )

    result = await RetrievedDocument.get_motor_collection().update_many(
        {"document_type": from_doc_type},
        {"$set": {"document_type": to_doc_type}},
    )
    logging.info(
        f"updating retdoc doc type from  {from_doc_type} to {to_doc_type} -> acknowledged={result.acknowledged} matched_count={result.matched_count} modified_count={result.modified_count}"  # noqa
    )


class Forward:
    @free_fall_migration(document_models=[RetrievedDocument, DocDocument])
    async def rename_doc_types(self, session):
        await update_doc_type("Covered Treatment List", "Medical Coverage List")


class Backward:
    ...
