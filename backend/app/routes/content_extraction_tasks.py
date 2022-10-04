from datetime import datetime, timezone

from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException, Security, status

from backend.app.routes.table_query import (
    TableFilterInfo,
    TableQueryResponse,
    TableSortInfo,
    get_query_json_list,
    query_table,
)
from backend.app.utils.logger import Logger, create_and_log, get_logger, update_and_log_diff
from backend.app.utils.user import get_current_user
from backend.common.models.content_extraction_task import (
    ContentExtractionResult,
    ContentExtractionTask,
    UpdateContentExtractionTask,
)
from backend.common.models.doc_document import DocDocument
from backend.common.models.user import User
from backend.common.services.extraction.extraction_delta import DeltaCreator

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


async def get_doc(doc_document_id: PydanticObjectId):
    return await DocDocument.get(doc_document_id)


@router.get(
    "/results/",
    response_model=TableQueryResponse,
    dependencies=[Security(get_current_user)],
)
async def read_extraction_results(
    extraction_id: PydanticObjectId,
    delta: bool = False,
    limit: int | None = None,
    skip: int | None = None,
    delta_subset: list[str] = Depends(get_query_json_list("delta_subset", str)),
    full_subset: list[str] = Depends(get_query_json_list("full_subset", str)),
    sorts: list[TableSortInfo] = Depends(get_query_json_list("sorts", TableSortInfo)),
    filters: list[TableFilterInfo] = Depends(get_query_json_list("filters", TableFilterInfo)),
):
    query = ContentExtractionResult.find({"content_extraction_task_id": extraction_id})
    if delta:
        if delta_subset:
            subsets = []
            if "add" in delta_subset:
                subsets.append({"add": True})
            if "remove" in delta_subset:
                subsets.append({"remove": True})
            if "edit" in delta_subset:
                subsets.append({"edit": {"$ne": None}})
            query = query.find({"$or": subsets})
        else:
            query = query.find({"$or": [{"add": True}, {"remove": True}, {"edit": {"$ne": None}}]})
    elif full_subset and full_subset != ["translated", "untranslated"]:
        if "translated" in full_subset:
            query = query.find({"translation.code": {"$ne": None}})
        else:
            query = query.find({"translation.code": None})

    res = await query_table(query, limit, skip, sorts, filters)

    if delta and "edit" in delta_subset:
        prevs = await ContentExtractionResult.find(
            {"_id": {"$in": [r.edit for r in res.data if r.edit]}}
        ).to_list()
        res.data = prevs + res.data

    return res


@router.get(
    "/",
    response_model=list[ContentExtractionTask],
    dependencies=[Security(get_current_user)],
)
async def read_extraction_tasks_for_doc(
    doc_document_id: PydanticObjectId,
):
    extraction_tasks: list[ContentExtractionTask] = (
        await ContentExtractionTask.find_many(
            ContentExtractionTask.doc_document_id == doc_document_id
        )
        .sort("-queued_time")
        .to_list()
    )
    return extraction_tasks


@router.post(
    "/{id}/delta",
    response_model=ContentExtractionTask,
    dependencies=[Security(get_current_user)],
)
async def create_extraction_delta(
    doc: DocDocument = Depends(get_doc),
    extract: ContentExtractionTask = Depends(get_target),
):
    if not doc.previous_doc_doc_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Document must have previous doc"
        )

    prev_doc = await DocDocument.get(doc.previous_doc_doc_id)
    if not prev_doc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Prev Document does not Exist"
        )

    if not prev_doc.content_extraction_task_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Prev Document must have Extraction"
        )

    prev_extract = await ContentExtractionTask.get(prev_doc.content_extraction_task_id)
    if not prev_extract:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Prev Document Extraction does not exist",
        )

    await DeltaCreator().compute_delta(extract, prev_extract)
    return extract


@router.get(
    "/{id}",
    response_model=ContentExtractionTask,
    dependencies=[Security(get_current_user)],
)
async def read_extraction_task(
    target: User = Depends(get_target),
):
    return target


@router.put(
    "/",
    response_model=ContentExtractionTask,
    status_code=status.HTTP_201_CREATED,
)
async def start_extraction_task(
    doc: DocDocument = Depends(get_doc),
    current_user: User = Security(get_current_user),
    logger: Logger = Depends(get_logger),
):
    extraction_task = ContentExtractionTask(
        initiator_id=current_user.id,
        doc_document_id=doc.id,
        queued_time=datetime.now(tz=timezone.utc),
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
    return updated
