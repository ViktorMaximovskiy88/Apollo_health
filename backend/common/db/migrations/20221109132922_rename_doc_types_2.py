import logging

from beanie import free_fall_migration

from backend.common.models.doc_document import DocDocument
from backend.common.models.document import RetrievedDocument
from backend.common.models.document_family import DocumentFamily
from backend.common.models.lineage import DocumentAnalysis


# there were 2 :p
async def update_doc_type(from_doc_type: str, to_doc_type: str):
    result = await DocDocument.get_motor_collection().update_many(
        {"document_type": from_doc_type},
        {"$set": {"document_type": to_doc_type}},
    )
    logging.info(
        f"updating DocDocument doc type from  {from_doc_type} to {to_doc_type} -> acknowledged={result.acknowledged} matched_count={result.matched_count} modified_count={result.modified_count}"  # noqa
    )

    result = await RetrievedDocument.get_motor_collection().update_many(
        {"document_type": from_doc_type},
        {"$set": {"document_type": to_doc_type}},
    )
    logging.info(
        f"updating RetrievedDocument doc type from  {from_doc_type} to {to_doc_type} -> acknowledged={result.acknowledged} matched_count={result.matched_count} modified_count={result.modified_count}"  # noqa
    )

    result = await DocumentFamily.get_motor_collection().update_many(
        {"document_type": from_doc_type},
        {"$set": {"document_type": to_doc_type}},
    )
    logging.info(
        f"updating DocumentFamily doc type from  {from_doc_type} to {to_doc_type} -> acknowledged={result.acknowledged} matched_count={result.matched_count} modified_count={result.modified_count}"  # noqa
    )

    result = await DocumentAnalysis.get_motor_collection().update_many(
        {"document_type": from_doc_type},
        {"$set": {"document_type": to_doc_type}},
    )
    logging.info(
        f"updating DocumentAnalysis doc type from  {from_doc_type} to {to_doc_type} -> acknowledged={result.acknowledged} matched_count={result.matched_count} modified_count={result.modified_count}"  # noqa
    )


class Forward:
    @free_fall_migration(
        document_models=[RetrievedDocument, DocDocument, DocumentFamily, DocumentAnalysis]
    )
    async def rename_doc_types(self, session):
        await update_doc_type("Newsletter", "Newsletter / Announcement")


class Backward:
    ...
