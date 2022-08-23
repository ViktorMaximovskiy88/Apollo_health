from datetime import datetime

from beanie import PydanticObjectId

from backend.app.routes.table_query import TableQueryResponse
from backend.common.models.doc_document import DocDocument, SiteDocDocument
from backend.common.models.shared import DocDocumentLocation
from backend.common.models.site_scrape_task import SiteScrapeTask


def get_one():
    pass


def get_list():
    pass


async def get_list_paged(
    match: dict | None = None,
    sort: dict | None = None,
    limit: int | None = None,
    skip: int | None = None,
) -> TableQueryResponse[SiteDocDocument]:

    pipeline = []

    if match:
        pipeline.append({"$match": match})

    total_query = await DocDocument.aggregate(
        aggregation_pipeline=[*pipeline, {"$count": "total"}],
    ).to_list()

    if sort:
        pipeline.append({"$sort": sort})

    if skip:
        pipeline.append({"$skip": skip})

    if limit:
        pipeline.append({"$limit": limit})

    data = await DocDocument.aggregate(
        aggregation_pipeline=pipeline,
        projection_model=SiteDocDocument,
    ).to_list()

    return TableQueryResponse(data=data, total=total_query[0]["total"])


async def get_site_list_paged(
    site_id: PydanticObjectId,
    match: dict | None = None,
    sort: dict | None = None,
    limit: int | None = None,
    skip: int | None = None,
) -> TableQueryResponse[SiteDocDocument]:

    pipeline = []
    pipeline.append({"$unwind": {"path": "$locations"}})

    if match:
        pipeline.append({"$match": match})

    pipeline.append({"$match": {"locations.site_id": site_id}})
    pipeline.append({"$replaceWith": {"$mergeObjects": ["$$ROOT", "$locations"]}})

    total_query = await DocDocument.aggregate(
        aggregation_pipeline=[*pipeline, {"$count": "total"}],
    ).to_list()

    if sort:
        pipeline.append({"$sort": sort})

    if skip:
        pipeline.append({"$skip": skip})

    if limit:
        pipeline.append({"$limit": limit})

    data = await DocDocument.aggregate(
        aggregation_pipeline=pipeline,
        projection_model=SiteDocDocument,
    ).to_list()

    return TableQueryResponse(data=data, total=total_query[0]["total"])


def calc_final_effective_date(doc: DocDocument, location: DocDocumentLocation) -> datetime:
    computeFromFields = []
    if doc.effective_date:
        computeFromFields.append(doc.effective_date)
    if doc.last_reviewed_date:
        computeFromFields.append(doc.last_reviewed_date)
    if doc.last_updated_date:
        computeFromFields.append(doc.last_updated_date)

    final_effective_date = (
        max(computeFromFields) if len(computeFromFields) > 0 else location.last_collected_date
    )

    return final_effective_date
