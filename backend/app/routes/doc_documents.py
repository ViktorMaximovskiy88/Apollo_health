import asyncio
from functools import reduce
from typing import List

from beanie import PydanticObjectId
from beanie.odm.queries.find import FindMany
from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.responses import StreamingResponse

from backend.app.core.settings import settings
from backend.app.routes.sites import Site
from backend.app.routes.table_query import (
    TableFilterInfo,
    TableQueryResponse,
    TableSortInfo,
    construct_table_query,
    get_query_json_list,
    query_table,
)
from backend.app.services.payer_backbone.payer_backbone_querier import (
    ControlledLivesResponse,
    PayerBackboneQuerier,
)
from backend.app.utils.user import get_current_user
from backend.common.models.base_document import BaseModel
from backend.common.models.doc_document import (
    BulkUpdateRequest,
    BulkUpdateResponse,
    DocDocument,
    DocDocumentView,
    IdOnlyDocument,
    UpdateDocDocument,
)
from backend.common.models.document_family import DocumentFamily
from backend.common.models.payer_backbone import PlanBenefit
from backend.common.models.payer_family import PayerFamily
from backend.common.models.shared import DocDocumentLocationView
from backend.common.models.site_scrape_task import SiteScrapeTask
from backend.common.models.tag_comparison import TagComparison
from backend.common.models.user import User
from backend.common.repositories.doc_document_repository import DocDocumentRepository
from backend.common.storage.client import DocumentStorageClient
from backend.common.tasks.task_queue import TaskQueue

router: APIRouter = APIRouter(
    prefix="/doc-documents",
    tags=["DocDocuments"],
)


task_queue = TaskQueue(
    queue_url=settings.task_worker_queue_url,
)


async def get_target(id: PydanticObjectId) -> DocDocument:
    task: DocDocument | None = await DocDocument.get(id)
    if not task:
        raise HTTPException(
            detail=f"Doc Document {id} Not Found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return task


@router.get(
    "/ids",
    response_model=list[PydanticObjectId],
    dependencies=[Security(get_current_user)],
)
async def get_all_doc_document_ids(
    site_id: PydanticObjectId | None = None,
    filters: list[TableFilterInfo] = Depends(get_query_json_list("filters", TableFilterInfo)),
):
    match = {"locations.site_id": site_id} if site_id else {}
    query = DocDocument.find_many(match).project(IdOnlyDocument)
    query = construct_table_query(query, [], filters)
    return [doc.id async for doc in query]


@router.get(
    "/",
    response_model=TableQueryResponse,
    dependencies=[Security(get_current_user)],
)
async def read_doc_documents(
    scrape_task_id: PydanticObjectId | None = None,
    limit: int | None = 50,
    skip: int | None = None,
    sorts: list[TableSortInfo] = Depends(get_query_json_list("sorts", TableSortInfo)),
    filters: list[TableFilterInfo] = Depends(get_query_json_list("filters", TableFilterInfo)),
) -> TableQueryResponse[DocDocument]:
    query = {}
    if scrape_task_id:
        task: SiteScrapeTask | None = await SiteScrapeTask.get(scrape_task_id)
        if not task:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Not able to retrieve tasks.")
        query["retrieved_document_id"] = {"$in": task.retrieved_document_ids}

    # query or none does not work.
    if query:
        document_query = DocDocument.find(query)
    else:
        document_query = DocDocument.find()

    docs = await query_table(document_query, limit, skip, as_aggregation=True)
    docs.data = [document_query.projection_model(**doc) for doc in docs.data]

    return docs


class CompareResponse(BaseModel):
    new_key: str | None = None
    prev_key: str | None = None
    tag_comparison: TagComparison | None = None
    exists: bool


@router.get(
    "/diff",
    dependencies=[Security(get_current_user)],
    response_model=CompareResponse,
)
async def get_diff(current_id: PydanticObjectId, prev_id: PydanticObjectId):
    doc_client = DocumentStorageClient()
    current_doc = await get_target(current_id)
    prev_doc = await get_target(prev_id)
    new_key = f"{current_doc.checksum}-{prev_doc.checksum}-new.pdf"
    prev_key = f"{current_doc.checksum}-{prev_doc.checksum}-prev.pdf"
    tag_comparison = await TagComparison.find_one(
        {"current_doc_id": current_doc.id, "prev_doc_id": prev_doc.id}
    )
    exists = (
        doc_client.object_exists(new_key)
        and doc_client.object_exists(prev_key)
        and tag_comparison is not None
    )
    return CompareResponse(
        new_key=new_key, prev_key=prev_key, exists=exists, tag_comparison=tag_comparison
    )


@router.get("/diff/{key}.pdf", dependencies=[Security(get_current_user)])
async def download_diff_document(key: str):
    client = DocumentStorageClient()
    stream = client.read_object_stream(f"{key}.pdf")
    return StreamingResponse(stream, media_type="application/pdf")


@router.get(
    "/{id}",
    response_model=DocDocumentView,
    dependencies=[Security(get_current_user)],
)
async def read_extraction_task(
    target: DocDocument = Depends(get_target),
) -> DocDocumentView:
    # https://roman-right.github.io/beanie/tutorial/relations/
    # Only top-level fields are fully supported for now
    # cant use relations... yet...
    site_ids: list[PydanticObjectId] = [location.site_id for location in target.locations]
    sites: List[Site] = await Site.find({"_id": {"$in": site_ids}}).to_list()
    doc: DocDocumentView = DocDocumentView(**target.dict())

    for site in sites:
        location: DocDocumentLocationView | None = doc.get_site_location(site.id)
        if location:
            location.site_name = site.name
        if location and location.payer_family_id:
            location.payer_family = await PayerFamily.get(location.payer_family_id)

    # TODO would love the ref/link here
    if doc.document_family_id:
        doc.document_family = await DocumentFamily.get(doc.document_family_id)

    return doc


@router.get(
    "/{id}/lives-by-controller",
    dependencies=[Security(get_current_user)],
    response_model=list[ControlledLivesResponse],
)
async def get_document_lives(
    target: DocDocument = Depends(get_target),
    effective_date: str | None = None,
):
    pbbq = None
    expressions = []
    payer_family_ids = [location.payer_family_id for location in target.locations]
    payer_families = PayerFamily.find({"_id": {"$in": payer_family_ids}})
    async for payer_family in payer_families:
        pbbq = PayerBackboneQuerier(payer_family, effective_date)
        plans = pbbq.construct_plan_benefit_query()
        expressions.append(reduce(lambda x, y: {**x, **y}, plans.find_expressions))
    if pbbq:
        plans = PlanBenefit.find({"$or": expressions})
        result = await pbbq.lives_by_controller(plans)
        return result
    return []


@router.post("/bulk", response_model=BulkUpdateResponse)
async def bulk_doc_type_update(
    body: BulkUpdateRequest,
    current_user: User = Security(get_current_user),
):
    targets: FindMany[DocDocument] = DocDocument.find_many({"_id": {"$in": body.ids}})
    update = body.update

    doc_documents_repo = DocDocumentRepository()

    counts, errors = {"suc": 0, "err": 0}, []

    async def gather_tasks(tasks):
        for res in await asyncio.gather(*tasks, return_exceptions=True):
            if isinstance(res, Exception):
                errors.append(str(res))
                counts["err"] += 1
            else:
                counts["suc"] += 1

    tasks = []
    async for doc in targets:
        full_update = update.copy()
        if body.payer_family_id:
            locations = []
            for location in doc.locations:
                if not body.site_id or body.site_id == location.site_id or body.all_sites:
                    locations.append(
                        location.copy(update={"payer_family_id": body.payer_family_id})
                    )
                else:
                    locations.append(location)
            full_update.locations = locations

        tasks.append(doc_documents_repo.execute(doc, full_update, current_user))
        if len(tasks) == 10:
            await gather_tasks(tasks)
            tasks = []
    await gather_tasks(tasks)

    return BulkUpdateResponse(count_success=counts["suc"], count_error=counts["err"], errors=errors)


@router.post("/{id}", response_model=DocDocument)
async def update_doc_document(
    updates: UpdateDocDocument,
    doc: DocDocument = Depends(get_target),
    current_user: User = Security(get_current_user),
):
    return await DocDocumentRepository().execute(doc, updates, current_user)
