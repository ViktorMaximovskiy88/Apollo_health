from beanie import free_fall_migration

from backend.common.core.enums import DocumentType
from backend.common.models.doc_document import DocDocument
from backend.common.models.document import RetrievedDocument
from backend.common.models.document_family import DocumentFamily
from backend.common.models.lineage import DocumentAnalysis


class Forward:
    @free_fall_migration(
        document_models=[DocDocument, DocumentFamily, RetrievedDocument, DocumentAnalysis]
    )
    async def change_internal_resource_to_internal_reference(self, session):

        InternalResource = "Internal Resource"

        # DocDocument
        await DocDocument.find(DocDocument.document_type == InternalResource).set(
            {DocDocument.document_type: DocumentType.InternalReference}
        )
        await DocDocument.find(DocDocument.doc_type_match.document_type == InternalResource).set(
            {DocDocument.doc_type_match.document_type: DocumentType.InternalReference}
        )

        # DocumentFamily
        await DocumentFamily.find(DocumentFamily.document_type == InternalResource).set(
            {DocumentFamily.document_type: DocumentType.InternalReference}
        )

        # RetrievedDocument
        await RetrievedDocument.find(RetrievedDocument.document_type == InternalResource).set(
            {RetrievedDocument.document_type: DocumentType.InternalReference}
        )
        await RetrievedDocument.find(
            RetrievedDocument.doc_type_match.document_type == InternalResource
        ).set({RetrievedDocument.doc_type_match.document_type: DocumentType.InternalReference})

        # DocumentAnalysis
        await DocumentAnalysis.find(DocumentAnalysis.document_type == InternalResource).set(
            {DocumentAnalysis.document_type: DocumentType.InternalReference}
        )


class Backward:
    pass
