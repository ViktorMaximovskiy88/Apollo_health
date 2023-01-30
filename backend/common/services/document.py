from typing import List

from beanie import PydanticObjectId

from backend.app.utils.logger import Logger, create_and_log
from backend.common.core.enums import ApprovalStatus
from backend.common.models.doc_document import DocDocument, DocDocumentLocation, SiteDocDocument
from backend.common.models.document import RetrievedDocument
from backend.common.models.document_analysis import DocumentAnalysisLineage
from backend.common.models.lineage import LineageDoc
from backend.common.models.shared import RetrievedDocumentLocation
from backend.common.models.user import User


def projection(site_id: PydanticObjectId):
    return [
        {"$set": {"site_id": site_id, "doc_document_id": "$_id"}},
        {
            "$project": {
                "retrieved_document_id": 1,
                "doc_document_id": 1,
                "site_id": 1,
                "classification_status": 1,
                "lineage_id": 1,
                "previous_doc_doc_id": 1,
                "is_current_version": 1,
            }
        },
    ]


# https://motor.readthedocs.io/en/stable/api-asyncio/asyncio_motor_collection.html?highlight=aggregate#motor.motor_asyncio.AsyncIOMotorCollection.aggregate
# https://www.mongodb.com/docs/manual/reference/method/db.collection.aggregate/#db.collection.aggregate--
async def get_site_docs(site_id: PydanticObjectId) -> list[DocumentAnalysisLineage]:
    cursor = DocDocument.get_motor_collection().aggregate(
        [
            {"$match": {"locations.site_id": site_id}},
            *projection(site_id),
        ],
        batchSize=25,
    )

    docs: List[DocumentAnalysisLineage] = []
    async for doc in cursor:
        docs.append(DocumentAnalysisLineage(**doc))
    return docs


async def get_site_docs_for_ids(
    site_id: PydanticObjectId, doc_ids: list[PydanticObjectId]
) -> list[SiteDocDocument]:
    cursor = DocDocument.get_motor_collection().aggregate(
        [
            {"$match": {"_id": {"$in": doc_ids}}},
            *projection(site_id),
        ],
        batchSize=25,
    )

    docs: List[DocumentAnalysisLineage] = []
    async for doc in cursor:
        docs.append(DocumentAnalysisLineage(**doc))
    return docs


async def get_site_lineage(site_id: PydanticObjectId):
    docs = await DocDocument.aggregate(
        aggregation_pipeline=[
            {"$match": {"locations.site_id": site_id}},
            {
                "$project": {
                    "_id": 1,
                    "name": 1,
                    "lineage_id": 1,
                    "previous_doc_doc_id": 1,
                    "retrieved_document_id": 1,
                    "is_current_version": 1,
                    "checksum": 1,
                    "file_extension": 1,
                    "document_type": 1,
                    "final_effective_date": 1,
                }
            },
        ],
        projection_model=LineageDoc,
    ).to_list()

    return docs


async def create_doc_document_service(
    retrieved_document: RetrievedDocument, user: User, doc_doc_fields: dict = {}
) -> DocDocument:
    # we always have one initially
    rt_doc_location: RetrievedDocumentLocation = retrieved_document.locations[0]
    doc_document: DocDocument = DocDocument(
        retrieved_document_id=retrieved_document.id,  # type: ignore
        name=retrieved_document.name,
        checksum=retrieved_document.checksum,
        text_checksum=retrieved_document.text_checksum,
        content_checksum=retrieved_document.content_checksum,
        document_type=retrieved_document.document_type,
        doc_type_confidence=retrieved_document.doc_type_confidence,
        doc_type_match=retrieved_document.doc_type_match,
        end_date=retrieved_document.end_date,
        effective_date=retrieved_document.effective_date,
        last_updated_date=retrieved_document.last_updated_date,
        last_reviewed_date=retrieved_document.last_reviewed_date,
        next_review_date=retrieved_document.next_review_date,
        next_update_date=retrieved_document.next_update_date,
        published_date=retrieved_document.published_date,
        lang_code=retrieved_document.lang_code,
        therapy_tags=retrieved_document.therapy_tags,
        indication_tags=retrieved_document.indication_tags,
        priority=retrieved_document.priority,
        file_extension=retrieved_document.file_extension,
        identified_dates=retrieved_document.identified_dates,
        last_collected_date=retrieved_document.last_collected_date,
        first_collected_date=retrieved_document.first_collected_date,
        lineage_id=retrieved_document.lineage_id,
        is_current_version=retrieved_document.is_current_version,
        locations=[DocDocumentLocation(**rt_doc_location.dict())],
        doc_vectors=retrieved_document.doc_vectors,
        file_size=retrieved_document.file_size,
        token_count=retrieved_document.token_count,
        is_searchable=retrieved_document.is_searchable,
    )
    # Since user uploaded doc and manually set doc info,
    # skip classification queue and set to approved.
    if retrieved_document.uploader_id:
        doc_document.classification_status = ApprovalStatus.APPROVED

    doc_document.set_final_effective_date()
    # Set doc doc specific fields which cannot be copied from retr doc.
    for doc_field_key, doc_field_value in doc_doc_fields.items():
        setattr(doc_document, doc_field_key, doc_field_value)

    logger: Logger = Logger()
    await create_and_log(logger, user, doc_document)

    return doc_document
