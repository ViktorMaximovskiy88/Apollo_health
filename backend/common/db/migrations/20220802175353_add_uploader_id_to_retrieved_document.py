from beanie import iterative_migration

from backend.common.models.document import RetrievedDocument


class Forward:
    @iterative_migration()
    async def add_uploader_id_to_retrieved_document(
        self, input_document: RetrievedDocument, output_document: RetrievedDocument
    ):
        if not input_document.uploader_id:
            output_document.uploader_id = None


class Backward:
    @iterative_migration()
    async def remove_uploader_id_from_retrieved_document(
        self, input_document: RetrievedDocument, output_document: RetrievedDocument
    ):
        output_document.uploader_id = None
