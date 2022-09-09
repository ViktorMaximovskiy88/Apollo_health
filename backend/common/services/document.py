from beanie import PydanticObjectId

from backend.common.models.document import RetrievedDocument, SiteRetrievedDocument


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
