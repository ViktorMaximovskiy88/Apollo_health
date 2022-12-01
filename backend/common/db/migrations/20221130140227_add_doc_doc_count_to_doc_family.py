import logging

from beanie import free_fall_migration

from backend.common.models.doc_document import DocDocument
from backend.common.models.document_family import DocumentFamily


class Forward:
    @free_fall_migration(document_models=[DocumentFamily])
    async def add_doc_doc_counts(self, session):
        async for document_family in DocumentFamily.find_all():
            count = await DocDocument.find({"document_family_id": document_family.id}).count()
            await DocumentFamily.get_motor_collection().find_one_and_update(
                {"_id": document_family.id},
                {"$set": {"doc_doc_count": count}},
            )
            logging.info(f'updating PayerFamily "{document_family.name}" doc count to {count}')


class Backward:
    ...
