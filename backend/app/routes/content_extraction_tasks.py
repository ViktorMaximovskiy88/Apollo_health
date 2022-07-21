from datetime import datetime
import json
from beanie import PydanticObjectId
from beanie.odm.operators.update.general import Set
from fastapi import APIRouter, Depends, HTTPException, Request, status, Security
from backend.app.routes.table_query import TableFilterInfo, TableQueryResponse, TableSortInfo, get_query_json_list, query_table
from backend.common.models.document import RetrievedDocument
from backend.common.models.site import Site

from backend.common.models.content_extraction_task import (
    ContentExtractionResult,
    ContentExtractionTask,
    UpdateContentExtractionTask,
)
from backend.common.models.user import User
from backend.app.utils.logger import (
    Logger,
    create_and_log,
    get_logger,
    update_and_log_diff,
)

from backend.app.utils.user import get_current_user

router = APIRouter(
    prefix="/extraction-tasks",
    tags=["ContentExtractionTasks"],
)


async def get_target(id: PydanticObjectId):
    task = await ContentExtractionTask.get(id)
    if not task:
        raise HTTPException(
            detail=f"Content Extraction Task {id} Not Found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return task

@router.get(
    "/results/",
    response_model=TableQueryResponse,
    dependencies=[Security(get_current_user)],
)
async def read_extraction_results(
    extraction_id: PydanticObjectId,
    limit: int | None = None,
    skip: int | None = None,
    sorts: list[TableSortInfo] = Depends(get_query_json_list('sorts', TableSortInfo)),
    filters: list[TableFilterInfo] = Depends(get_query_json_list('filters', TableFilterInfo))
):
    query = ContentExtractionResult.find({'content_extraction_task_id': extraction_id})
    return await query_table(query, limit, skip, sorts, filters)


@router.get(
    "/",
    response_model=list[ContentExtractionTask],
    dependencies=[Security(get_current_user)],
)
async def read_extraction_tasks_for_doc(
    retrieved_document_id: PydanticObjectId,
):
    extraction_tasks: list[ContentExtractionTask] = (
        await ContentExtractionTask.find_many(
            ContentExtractionTask.retrieved_document_id == retrieved_document_id
        )
        .sort("-queued_time")
        .to_list()
    )
    return extraction_tasks


@router.get(
    "/{id}",
    response_model=ContentExtractionTask,
    dependencies=[Security(get_current_user)],
)
async def read_extraction_task(
    target: User = Depends(get_target),
):
    return target


async def get_doc(retrieved_document_id: PydanticObjectId):
    return await RetrievedDocument.get(retrieved_document_id)


@router.put(
    "/",
    response_model=ContentExtractionTask,
    status_code=status.HTTP_201_CREATED,
)
async def start_extraction_task(
    doc: RetrievedDocument = Depends(get_doc),
    current_user: User = Security(get_current_user),
    logger: Logger = Depends(get_logger),
):
    extraction_task = ContentExtractionTask(
        site_id=doc.site_id,
        scrape_task_id=doc.scrape_task_id,
        retrieved_document_id=doc.id,
        queued_time=datetime.now(),
    )

    await create_and_log(logger, current_user, extraction_task)
    return extraction_task


@router.post("/{id}", response_model=ContentExtractionTask)
async def update_extraction_task(
    updates: UpdateContentExtractionTask,
    target: ContentExtractionTask = Depends(get_target),
    current_user: User = Security(get_current_user),
    logger: Logger = Depends(get_logger),
):
    # NOTE: Could use a transaction here
    updated = await update_and_log_diff(logger, current_user, target, updates)
    await Site.find_one(Site.id == target.site_id).update(
        Set({Site.last_run_status: updates.status}),
    )
    return updated
