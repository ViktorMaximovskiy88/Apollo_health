from beanie import PydanticObjectId

from backend.common.models.document import RetrievedDocument, SiteRetrievedDocument
from backend.common.models.lineage import LineageDoc


async def get_site_docs(site_id: PydanticObjectId) -> list[SiteRetrievedDocument]:
    docs = await RetrievedDocument.aggregate(
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
    docs = await RetrievedDocument.aggregate(
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


async def get_site_lineage(site_id: PydanticObjectId):
    docs = await RetrievedDocument.aggregate(
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
