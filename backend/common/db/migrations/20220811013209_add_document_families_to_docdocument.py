import logging

from beanie import free_fall_migration

from backend.common.models.doc_document import DocDocument


class Forward:
    @free_fall_migration([DocDocument])
    async def add_document_families_to_docdocument(self, session):
        await DocDocument.get_motor_collection().update_many(
            {"document_family": None}, {"$set": {"document_family": []}}
        )


class Backward:
    @free_fall_migration([DocDocument])
    async def add_document_families_to_docdocument(self, session):
        logging.info("there is no undo here")
        pass
