from beanie import iterative_migration

from backend.common.models.doc_document import DocDocument, NoDocumentFamiliesDocDocument


class Forward:
    @iterative_migration()
    async def add_document_families_to_docdocument(
        self, input_document: NoDocumentFamiliesDocDocument, output_document: DocDocument
    ):
        if input_document.document_families:
            output_document.document_families = input_document.document_families
        else:
            output_document.document_families = []


class Backward:
    @iterative_migration()
    async def remove_document_families_from_docdocument(
        self, input_document: DocDocument, output_document: NoDocumentFamiliesDocDocument
    ):
        if len(input_document.document_families) > 0:
            # preserve document family data if exists
            output_document.document_families = input_document.document_families
        else:
            output_document.document_families = None
