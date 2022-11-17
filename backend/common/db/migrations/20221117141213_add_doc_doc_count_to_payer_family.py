import logging

from beanie import free_fall_migration

from backend.common.models.doc_document import DocDocument
from backend.common.models.payer_family import PayerFamily


class Forward:
    @free_fall_migration(document_models=[PayerFamily])
    async def add_doc_doc_counts(self, session):
        payer_families = await PayerFamily.find_all().to_list()
        doc_documents = await DocDocument.find_all().to_list()
        payer_family_counts = {}
        for doc_document in doc_documents:
            for location in doc_document.locations:
                payer_family_id = location.payer_family_id
                if not payer_family_id:
                    continue
                if payer_family_id not in payer_family_counts:
                    payer_family_counts[payer_family_id] = 1
                    continue
                payer_family_counts[payer_family_id] += 1
        for payer_family in payer_families:
            old_doc_doc_count = payer_family.doc_doc_count
            doc_doc_count = 0
            if payer_family.id in payer_family_counts:
                doc_doc_count = payer_family_counts[payer_family.id]
            await PayerFamily.get_motor_collection().find_one_and_update(
                {"_id": payer_family.id},
                {"$set": {"doc_doc_count": doc_doc_count}},
            )
            logging.info(
                f'updating PayerFamily "{payer_family.name}" property doc_doc_count from  {old_doc_doc_count} to {doc_doc_count}'  # noqa
            )


class Backward:
    ...
