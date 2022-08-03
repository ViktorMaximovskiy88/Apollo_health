from beanie import iterative_migration

from backend.common.models.document import RetrievedDocument


class Forward:
    @iterative_migration()
    async def add_user_id_to_retrieved_document(
        self, input_document: RetrievedDocument, output_document: RetrievedDocument
    ):
        if not input_document.user_id:
            output_document.user_id = None


class Backward:
    @iterative_migration()
    async def remove_user_id_from_retrieved_document(
        self, input_document: RetrievedDocument, output_document: RetrievedDocument
    ):
        output_document.user_id = None
