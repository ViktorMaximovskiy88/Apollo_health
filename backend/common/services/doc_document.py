from beanie import PydanticObjectId

from backend.common.models.base_document import BaseModel
from backend.common.models.doc_document import DocDocument, SiteDocDocument


class PagedCount(BaseModel):
    checksum: int


async def get_site_doc_doc_table(
    site_id: PydanticObjectId,
    retrieved_document_ids: list[PydanticObjectId],
    filters: list[dict],
    sorts: list[dict],
    limit: int = 50,
    skip: int = 0,
) -> list[SiteDocDocument]:
    pipeline = []

    if len(retrieved_document_ids) > 0:
        pipeline.append({"$match": {"retrieved_document_id": {"$in": retrieved_document_ids}}})

    pipeline.append({"$match": {"locations.site_id": site_id}})

    pipeline += [
        {"$unwind": {"path": "$locations"}},
        {"$replaceRoot": {"newRoot": {"$mergeObjects": ["$$ROOT", "$locations"]}}},
        {"$match": {"site_id": site_id}},
    ]

    for filter in filters:
        pipeline.append({"$match": filter})

    pipeline.append({"$unset": ["locations"]})

    count_pipeline = pipeline[:]
    count_pipeline.append({"$count": "checksum"})
    count_result = await DocDocument.aggregate(
        aggregation_pipeline=count_pipeline,
        projection_model=PagedCount,
    ).to_list()

    if len(sorts) > 0:
        sort_by = {}
        for (name, direction) in sorts:
            sort_by[name] = direction
        pipeline.append({"$sort": sort_by})

    pipeline.append({"$skip": skip})
    pipeline.append({"$limit": limit})

    docs = await DocDocument.aggregate(
        aggregation_pipeline=pipeline,
        projection_model=SiteDocDocument,
    ).to_list()

    return docs, count_result[0].checksum
