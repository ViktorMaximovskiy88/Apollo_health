from datetime import datetime, timedelta, timezone
from typing import Any, Type

from beanie import PydanticObjectId
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Security, status
from pydantic import Field
from pymongo import ReturnDocument

import backend.common.models as collection_classes
from backend.app.routes.table_query import (
    TableFilterInfo,
    TableQueryResponse,
    TableSortInfo,
    construct_table_query,
    get_query_json_list,
    query_table,
)
from backend.app.utils.logger import Logger, create_and_log, get_logger, update_and_log_diff
from backend.app.utils.user import get_current_user
from backend.common.models.base_document import BaseDocument, BaseModel
from backend.common.models.comment import Comment, HoldType
from backend.common.models.doc_document import (
    DocDocument,
    LockableDocument,
    TaskLock,
    UpdateDocDocument,
)
from backend.common.models.user import User
from backend.common.models.work_queue import WorkQueue, WorkQueueLog, WorkQueueUpdate
from backend.common.repositories.doc_document_repository import DocDocumentRepository

router = APIRouter(
    prefix="/work-queues",
    tags=["WorkQueues"],
)


async def get_target(id: PydanticObjectId):
    queue = await WorkQueue.get(id)
    if not queue:
        raise HTTPException(
            detail=f"Work Queue {id} Not Found", status_code=status.HTTP_404_NOT_FOUND
        )
    return queue


@router.get("/", response_model=list[WorkQueue])
async def read_work_queues(
    current_user: User = Security(get_current_user),
):
    queues: list[WorkQueue] = await WorkQueue.find_many({}).to_list()
    return queues


@router.get("/counts")
async def read_work_queue_counts(
    current_user: User = Security(get_current_user),
):
    response = []

    queues = WorkQueue.find_many({})
    async for work_queue in queues:
        Collection: BaseDocument = getattr(collection_classes, work_queue.collection_name)
        count = await Collection.find(work_queue.document_query).count()
        response.append({"work_queue_id": work_queue.id, "count": count})

    return response


@router.get(
    "/search",
    dependencies=[Security(get_current_user)],
    response_model=WorkQueue,
)
async def read_work_queue_by_name(
    name: str,
):
    work_queue = await WorkQueue.find_one({"name": name})
    return work_queue


@router.get("/{id}", response_model=WorkQueue)
async def read_work_queue(
    target: WorkQueue = Depends(get_target),
    current_user: User = Security(get_current_user),
):
    return target


@router.put("/", response_model=WorkQueue, status_code=status.HTTP_201_CREATED)
async def create_work_queue(
    work_queue: WorkQueue,
    current_user: User = Security(get_current_user),
    logger: Logger = Depends(get_logger),
):
    new_queue = WorkQueue(
        name=work_queue.name,
        frontend_component=work_queue.frontend_component,
        collection_name=work_queue.collection_name,
        update_model_name=work_queue.update_model_name,
        document_query=work_queue.document_query,
        user_query=work_queue.user_query,
        submit_actions=work_queue.submit_actions,
    )
    await create_and_log(logger, current_user, new_queue)
    return new_queue


@router.post("/{id}", response_model=WorkQueue)
async def update_queue(
    updates: WorkQueueUpdate,
    target: WorkQueue = Depends(get_target),
    current_user: User = Security(get_current_user),
    logger: Logger = Depends(get_logger),
):
    updated = await update_and_log_diff(logger, current_user, target, updates)
    return updated


class IdOnlyDocument(BaseModel):
    id: PydanticObjectId = Field(None, alias="_id")


class LocationSubDocument(BaseModel):
    site_id: PydanticObjectId
    link_text: str | None


class IdNameLockOnlyDocument(IdOnlyDocument):
    name: str
    document_type: str | None = None
    final_effective_date: datetime | None = None
    first_collected_date: datetime | None = None
    locations: list[LocationSubDocument] = []
    locks: list[TaskLock] = []
    priority: int = 0
    hold_type: str | None = None
    hold_time: datetime | None = None
    hold_comment: str | None = None


def combine_queue_query_with_user_query(
    work_queue: WorkQueue, sorts: list[TableSortInfo], filters: list[TableFilterInfo]
):
    Collection: BaseDocument = getattr(collection_classes, work_queue.collection_name)
    query = (
        Collection.find(work_queue.document_query)
        .sort(*work_queue.sort_query)
        .project(IdNameLockOnlyDocument)
    )
    for filter in filters:
        if filter.name == "locks.user_id" and filter.value:
            now = str(datetime.now(tz=timezone.utc))
            filters.append(
                TableFilterInfo(name="locks.expires", operator="after", type="date", value=now)
            )

    return construct_table_query(query, sorts, filters)


async def get_hold_comment(id: PydanticObjectId, type: str):
    return await (
        Comment.find(
            Comment.target_id == id,
            Comment.type == type,
        )
        .sort("-time")
        .limit(1)
    ).first_or_none()


@router.get(
    "/{id}/items",
    response_model=TableQueryResponse,
    dependencies=[Security(get_current_user)],
)
async def get_work_queue_items(
    work_queue: WorkQueue = Depends(get_target),
    limit: int | None = None,
    skip: int | None = None,
    sorts: list[TableSortInfo] = Depends(get_query_json_list("sorts", TableSortInfo)),
    filters: list[TableFilterInfo] = Depends(get_query_json_list("filters", TableFilterInfo)),
):
    query = combine_queue_query_with_user_query(work_queue, sorts, filters)
    res = await query_table(query, limit, skip)
    if "Hold" in work_queue.name:
        for doc in res.data:
            comment = await get_hold_comment(doc.id, work_queue.name)
            if comment:
                doc.hold_comment = comment.text
                doc.hold_time = comment.time
    return res


class TakeLockResponse(BaseModel):
    acquired_lock: bool
    lock: TaskLock | None = None


class TakeNextWorkQueueResponse(BaseModel):
    acquired_lock: bool
    item_id: PydanticObjectId | None = None


def get_valid_lock(locks: list[Any], work_queued_id: PydanticObjectId | None, now: datetime):
    return next(
        filter(
            lambda lock: lock.work_queue_id == work_queued_id
            and lock.expires.now(tz=timezone.utc) > now,
            locks,
        ),
        None,
    )


async def attempt_lock_acquire(
    work_queue: WorkQueue,
    item_id: PydanticObjectId,
    current_user: User,
    expiry_time: datetime | None = None,
):
    Collection: Type[BaseDocument] = getattr(collection_classes, work_queue.collection_name)
    grace = work_queue.grace_period

    now = datetime.now(tz=timezone.utc)
    if not expiry_time:
        expiry_time = now + timedelta(seconds=grace)
    await Collection.find_one({"_id": item_id}).update(
        {"$pull": {"locks": {"expires": {"$lt": now}}}}
    )

    # Check if you already own the lock, if so just bump the expiry
    already_owned = await Collection.get_motor_collection().find_one_and_update(
        {
            "_id": item_id,
            "locks": {
                "$elemMatch": {
                    "work_queue_id": work_queue.id,
                    "user_id": current_user.id,
                    "expires": {"$gt": now},
                }
            },
        },
        {
            "$max": {"locks.$.expires": expiry_time},
        },
        projection={"locks": 1},
        return_document=ReturnDocument.AFTER,
    )
    if already_owned:
        item = LockableDocument.parse_obj(already_owned)
        lock = get_valid_lock(item.locks, work_queue.id, now)
        return TakeLockResponse(acquired_lock=True, lock=lock)

    # Check if anyone owns the lock, if not take it
    acquired = await Collection.get_motor_collection().find_one_and_update(
        {
            "_id": item_id,
            "locks": {
                "$not": {"$elemMatch": {"work_queue_id": work_queue.id, "expires": {"$gt": now}}}
            },
        },
        {
            "$addToSet": {
                "locks": {
                    "work_queue_id": work_queue.id,
                    "expires": expiry_time,
                    "user_id": current_user.id,
                }
            },
        },
        projection={"locks": 1},
        return_document=ReturnDocument.AFTER,
    )
    if acquired:
        item = LockableDocument.parse_obj(acquired)
        lock = get_valid_lock(item.locks, work_queue.id, now)
        return TakeLockResponse(acquired_lock=True, lock=lock)

    item: LockableDocument | None = await Collection.find_one({"_id": item_id}).project(
        LockableDocument
    )
    if not item:
        raise HTTPException(
            detail=f"{work_queue.collection_name} {item_id} Not Found",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    lock = get_valid_lock(item.locks, item_id, now)
    return TakeLockResponse(acquired_lock=False, lock=lock)


@router.post("/{id}/items/take-next", response_model=TakeNextWorkQueueResponse)
async def take_next_work_item(
    filter: list[TableFilterInfo] = [],
    sort: TableSortInfo | list[TableSortInfo] = [],
    work_queue: WorkQueue = Depends(get_target),
    current_user: User = Security(get_current_user),
):
    now = datetime.now(tz=timezone.utc)
    unclaimed_query = {
        "locks": {"$not": {"$elemMatch": {"work_queue_id": work_queue.id, "expires": {"$gt": now}}}}
    }
    if isinstance(sort, TableSortInfo):
        sort = [sort]
    query = combine_queue_query_with_user_query(work_queue, sort, filter)
    query = query.find(unclaimed_query)
    item = await query.project(IdOnlyDocument).first_or_none()
    if item and item.id:
        lock = await attempt_lock_acquire(work_queue, item.id, current_user)
        if lock.acquired_lock:
            return TakeNextWorkQueueResponse(acquired_lock=True, item_id=item.id)

    return TakeNextWorkQueueResponse(acquired_lock=False)


@router.post("/{id}/items/{item_id}/take", response_model=TakeLockResponse)
async def take_work_item(
    item_id: PydanticObjectId,
    work_queue: WorkQueue = Depends(get_target),
    current_user: User = Security(get_current_user),
):
    return await attempt_lock_acquire(work_queue, item_id, current_user)


class SubmitWorkItemResponse(BaseModel):
    success: bool


class SubmitWorkItemRequest(BaseModel):
    action_label: str
    updates: dict[str, Any]
    reassignment: PydanticObjectId | None
    comment: str | None
    hold_type: str | None
    type: HoldType | None


@router.post("/{id}/items/{item_id}/submit", response_model=SubmitWorkItemResponse)
async def submit_work_item(
    body: SubmitWorkItemRequest,
    item_id: PydanticObjectId,
    background_tasks: BackgroundTasks,
    logger: Logger = Depends(get_logger),
    work_queue: WorkQueue = Depends(get_target),
    current_user: User = Security(get_current_user),
):
    Collection: Type[BaseDocument] = getattr(collection_classes, work_queue.collection_name)
    UpdateModel: Type[BaseDocument] = getattr(collection_classes, work_queue.update_model_name)

    lock = await attempt_lock_acquire(work_queue, item_id, current_user)
    if not lock.acquired_lock:
        return SubmitWorkItemResponse(success=False)

    item = await Collection.get(item_id)
    if not item:
        raise HTTPException(detail=f"{item_id} Not Found", status_code=status.HTTP_404_NOT_FOUND)
    action = next(filter(lambda a: a.label == body.action_label, work_queue.submit_actions), None)
    # TODO adding None to prevent StopIteration, does the logic still work?
    # raise?
    if action and action.reassignable and action.dest_queue and body.reassignment:
        dest_user = await User.get(body.reassignment)
        dest_queue = await WorkQueue.find_one(WorkQueue.name == action.dest_queue)
        if dest_queue and dest_user:
            expires = datetime.now(tz=timezone.utc) + timedelta(days=365)
            await attempt_lock_acquire(dest_queue, item_id, dest_user, expires)

    now = datetime.now(tz=timezone.utc)
    if body.comment:
        comment = Comment(
            target_id=item_id,
            user_id=current_user.id,  # type: ignore
            time=now,
            text=body.comment,
            type=body.type,
        )
        await comment.save()

    updates = UpdateModel.parse_obj(body.updates)

    if isinstance(item, DocDocument) and isinstance(updates, UpdateDocDocument):
        await DocDocumentRepository().execute(item, updates, current_user)
    else:
        await update_and_log_diff(logger, current_user, item, updates)

    await Collection.find_one({"_id": item_id}).update(
        {"$pull": {"locks": {"work_queue_id": work_queue.id}}}
    )

    await WorkQueueLog(
        queue_id=work_queue.id,  # type: ignore
        queue_name=work_queue.name,
        item_id=item_id,
        action=body.action_label,
        user_id=current_user.id,  # type: ignore
        submitted_at=now,
    ).save()

    return SubmitWorkItemResponse(success=True)
