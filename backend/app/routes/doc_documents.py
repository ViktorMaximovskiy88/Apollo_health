from datetime import datetime, timedelta, timezone
from typing import List

from beanie import PydanticObjectId
from beanie.odm.queries.find import FindMany
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Security, status
from fastapi.responses import StreamingResponse

from backend.app.routes.sites import Site
from backend.app.routes.table_query import (
    TableFilterInfo,
    TableQueryResponse,
    TableSortInfo,
    get_query_json_list,
    query_table,
)
from backend.app.utils.logger import Logger, get_logger, update_and_log_diff
from backend.app.utils.user import get_current_user
from backend.common.models.base_document import BaseModel
from backend.common.models.doc_document import (
    DocDocument,
    DocDocumentLimitTags,
    DocDocumentView,
    UpdateDocDocument,
)
from backend.common.models.document_mixins import calc_final_effective_date
from backend.common.models.shared import DocDocumentLocationView
from backend.common.models.site_scrape_task import SiteScrapeTask
from backend.common.models.user import User
from backend.common.services.doc_lifecycle.hooks import doc_document_save_hook, get_doc_change_info
from backend.common.services.lineage.update_prev_document import update_lineage
from backend.common.services.text_compare.doc_text_compare import DocTextCompare
from backend.common.storage.client import DocumentStorageClient

router: APIRouter = APIRouter(
    prefix="/doc-documents",
    tags=["DocDocuments"],
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
    "/",
    response_model=TableQueryResponse,
    dependencies=[Security(get_current_user)],
)
async def read_doc_documents(
    scrape_task_id: PydanticObjectId | None = None,
    limit: int | None = None,
    skip: int | None = None,
    sorts: list[TableSortInfo] = Depends(get_query_json_list("sorts", TableSortInfo)),
    filters: list[TableFilterInfo] = Depends(get_query_json_list("filters", TableFilterInfo)),
) -> TableQueryResponse[DocDocumentLimitTags]:
    query = {}
    if scrape_task_id:
        task: SiteScrapeTask | None = await SiteScrapeTask.get(scrape_task_id)
        if not task:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Not able to retrieve tasks.")
        query["retrieved_document_id"] = {"$in": task.retrieved_document_ids}
    document_query: FindMany[DocDocumentLimitTags] = DocDocument.find(query).project(
        DocDocumentLimitTags
    )
    return await query_table(document_query, limit, skip, sorts, filters)


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

    return doc


class CompareResponse(BaseModel):
    exists: bool
    processing: bool
    queued: bool = False
    new_key: str | None = None
    prev_key: str | None = None


@router.post(
    "/diff/{id}",
    response_model=CompareResponse,
    dependencies=[Security(get_current_user)],
)
async def create_diff(
    previous_doc_doc_id: PydanticObjectId,
    background_tasks: BackgroundTasks,
    current_doc: DocDocument = Depends(get_target),
):
    five_mins_ago = datetime.now(tz=timezone.utc) - timedelta(minutes=5)
    if (
        current_doc.compare_create_time
        and current_doc.compare_create_time.replace(tzinfo=timezone.utc) > five_mins_ago
    ):
        # Do not requeue if creation queued in past five mins
        return CompareResponse(exists=False, processing=True)
    prev_doc: DocDocument = await get_target(previous_doc_doc_id)
    doc_client = DocumentStorageClient()
    new_key = f"{current_doc.checksum}-{prev_doc.checksum}-new.pdf"
    prev_key = f"{current_doc.checksum}-{prev_doc.checksum}-prev.pdf"
    if doc_client.object_exists(new_key) and doc_client.object_exists(prev_key):
        return CompareResponse(exists=True, processing=False, new_key=new_key, prev_key=prev_key)
    else:
        dtc = DocTextCompare(doc_client)
        background_tasks.add_task(dtc.compare, doc=current_doc, prev_doc=prev_doc)
        current_doc.compare_create_time = datetime.now(tz=timezone.utc)
        await current_doc.save()
        return CompareResponse(exists=False, processing=True, queued=True)


@router.post("/{id}", response_model=DocDocument)
async def update_doc_document(
    updates: UpdateDocDocument,
    background_tasks: BackgroundTasks,
    doc: DocDocument = Depends(get_target),
    current_user: User = Security(get_current_user),
    logger: Logger = Depends(get_logger),
):
    updates.final_effective_date = calc_final_effective_date(updates)
    change_info = get_doc_change_info(updates, doc)
    old_previous_doc_doc_id = doc.previous_doc_doc_id
    updated = await update_and_log_diff(logger, current_user, doc, updates)
    await update_lineage(
        updating_doc_doc=doc,
        old_prev_doc_doc_id=old_previous_doc_doc_id,
        new_prev_doc_doc_id=updates.previous_doc_doc_id,
    )
    await doc_document_save_hook(doc, change_info)
    return updated
