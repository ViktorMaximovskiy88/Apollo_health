from beanie import free_fall_migration

from backend.common.core.enums import DocumentType
from backend.common.models.doc_document import DocDocument
from backend.common.models.document import RetrievedDocument
from backend.common.models.document_analysis import DocumentAnalysis
from backend.common.models.document_family import DocumentFamily


class Forward:
    @free_fall_migration(
        document_models=[DocDocument, DocumentFamily, RetrievedDocument, DocumentAnalysis]
    )
    async def change_internal_resource_to_internal_reference(self, session):

        internal_resource = "Internal Resource"

        # DocDocument
        await DocDocument.find({"document_type": internal_resource}).update_many(
            {"$set": {"document_type": DocumentType.InternalReference}}
        )
        await DocDocument.find({"doc_type_match.document_type": internal_resource}).update_many(
            {"$set": {"doc_type_match.document_type": DocumentType.InternalReference}}
        )

        # DocumentFamily
        await DocumentFamily.find({"document_type": internal_resource}).update_many(
            {"$set": {"document_type": DocumentType.InternalReference}}
        )

        # RetrievedDocument
        await RetrievedDocument.find({"document_type": internal_resource}).update_many(
            {"$set": {"document_type": DocumentType.InternalReference}}
        )
        await RetrievedDocument.find(
            {"doc_type_match.document_type": internal_resource}
        ).update_many({"$set": {"doc_type_match.document_type": DocumentType.InternalReference}})

        # DocumentAnalysis
        await DocumentAnalysis.find({"document_type": internal_resource}).update_many(
            {"$set": {"document_type": DocumentType.InternalReference}}
        )


class Backward:
    pass
