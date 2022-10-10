from typing import List

from beanie import PydanticObjectId

from backend.app.utils.logger import Logger, create_and_log
from backend.common.models.doc_document import DocDocument, DocDocumentLocation
from backend.common.models.document import RetrievedDocument, SiteRetrievedDocument
from backend.common.models.lineage import LineageDoc
from backend.common.models.shared import RetrievedDocumentLocation
from backend.common.models.user import User


async def get_site_docs(site_id: PydanticObjectId) -> list[SiteRetrievedDocument]:
    docs: List[SiteRetrievedDocument] = await RetrievedDocument.aggregate(
        aggregation_pipeline=[
            {"$match": {"locations.site_id": site_id}},
            {"$unwind": {"path": "$locations"}},
            {"$replaceRoot": {"newRoot": {"$mergeObjects": ["$$ROOT", "$locations"]}}},
            {"$match": {"site_id": site_id}},
            {"$unset": ["locations"]},
        ],
        projection_model=SiteRetrievedDocument,
    ).to_list()

    return docs


async def get_site_docs_for_ids(
    site_id: PydanticObjectId, doc_ids: list[PydanticObjectId]
) -> list[SiteRetrievedDocument]:
    docs: List[SiteRetrievedDocument] = await RetrievedDocument.aggregate(
        aggregation_pipeline=[
            {"$match": {"_id": {"$in": doc_ids}}},
            {"$unwind": {"path": "$locations"}},
            {"$replaceRoot": {"newRoot": {"$mergeObjects": ["$$ROOT", "$locations"]}}},
            {"$match": {"site_id": site_id}},
            {"$unset": ["locations"]},
        ],
        projection_model=SiteRetrievedDocument,
    ).to_list()

    return docs


async def get_site_lineage(site_id: PydanticObjectId) -> List[LineageDoc]:
    docs: List[LineageDoc] = await RetrievedDocument.aggregate(
        aggregation_pipeline=[
            {"$match": {"locations.site_id": site_id}},
            {
                "$set": {
                    "final_effective_date": {
                        "$ifNull": [
                            {
                                "$max": [
                                    "$effective_date",
                                    "$last_reviewed_date",
                                    "$last_updated_date",
                                ]
                            },
                            "$first_collected_date",
                        ]
                    }
                }
            },
            {
                "$project": {
                    "_id": 1,
                    "name": 1,
                    "lineage_id": 1,
                    "previous_doc_id": 1,
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
    retrieved_document: RetrievedDocument,
    user: User,
) -> DocDocument:
    # we always have one initially
    rt_doc_location: RetrievedDocumentLocation = retrieved_document.locations[0]
    doc_document: DocDocument = DocDocument(
        retrieved_document_id=retrieved_document.id,  # type: ignore
        name=retrieved_document.name,
        checksum=retrieved_document.checksum,
        text_checksum=retrieved_document.text_checksum,
        document_type=retrieved_document.document_type,
        doc_type_confidence=retrieved_document.doc_type_confidence,
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
        file_extension=retrieved_document.file_extension,
        identified_dates=retrieved_document.identified_dates,
        last_collected_date=retrieved_document.last_collected_date,
        first_collected_date=retrieved_document.first_collected_date,
        locations=[DocDocumentLocation(**rt_doc_location.dict())],
    )

    doc_document.set_final_effective_date()
    logger: Logger = Logger()
    await create_and_log(logger, user, doc_document)

    return doc_document
