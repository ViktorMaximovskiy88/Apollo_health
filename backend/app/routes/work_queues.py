import asyncio
import datetime
from typing import Any, Type
from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException, Security, status
from pydantic import BaseModel, Field
from backend.app.routes.table_query import TableFilterInfo, TableQueryResponse, TableSortInfo, get_query_json_list, query_table
from backend.common.models.base_document import BaseDocument
from pymongo import ReturnDocument
from backend.common.models.comment import Comment
from backend.common.models.doc_document import LockableDocument, TaskLock
from backend.common.models.user import User
import backend.common.models as collection_classes
from backend.app.utils.logger import (
    Logger,
    create_and_log,
    get_logger,
    update_and_log_diff,
)
from backend.app.utils.user import get_current_user
from backend.common.models.work_queue import WorkQueue, WorkQueueUpdate

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
        response.append({ 'work_queue_id': work_queue.id, 'count': count })

    return response

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
    id: PydanticObjectId = Field(None, alias='_id')

class IdNameLockOnlyDocument(IdOnlyDocument):
    name: str
    locks: list[TaskLock] = []

@router.get("/{id}/items", response_model=TableQueryResponse)
async def get_work_queue_items(
    work_queue: WorkQueue = Depends(get_target),
    current_user: User = Security(get_current_user),
    limit: int | None = None,
    skip: int | None = None,
    sorts: list[TableSortInfo] = Depends(get_query_json_list("sorts", TableSortInfo)),
    filters: list[TableFilterInfo] = Depends(
        get_query_json_list("filters", TableFilterInfo)
    ),
):
    Collection: BaseDocument = getattr(collection_classes, work_queue.collection_name)
    query = Collection.find(work_queue.document_query).sort(*work_queue.sort_query).project(IdNameLockOnlyDocument)
    for filter in filters:
        if filter.name == 'locks.user_id' and filter.value:
            now = str(datetime.datetime.now())
            filters.append(TableFilterInfo(name='locks.expires', operator='after', type='date', value=now))
    return await query_table(query, limit, skip, sorts, filters)

class TakeLockResponse(BaseModel):
    acquired_lock: bool
    lock: TaskLock | None = None

class TakeNextWorkQueueResponse(BaseModel):
    acquired_lock: bool
    item_id: PydanticObjectId | None = None

async def attempt_lock_acquire(work_queue: WorkQueue, item_id: PydanticObjectId, current_user: User, expiry_time: datetime.datetime | None = None):
    Collection: Type[BaseDocument] = getattr(collection_classes, work_queue.collection_name)
    grace = work_queue.grace_period

    now = datetime.datetime.now()
    if not expiry_time:
        expiry_time = now + datetime.timedelta(seconds=grace)
    await Collection.find_one({ '_id': item_id }).update({ '$pull': { 'locks': { 'expires': { '$lt': now } } } })

    # Check if you already own the lock, if so just bump the expiry
    already_owned = await Collection.get_motor_collection().find_one_and_update(
        {
            '_id': item_id,
            'locks': {
                '$elemMatch': {
                    'work_queue_id': work_queue.id,
                    'user_id': current_user.id,
                    'expires': { '$gt': now }
                }
            }
        },
        {
            '$max': { 'locks.$.expires': expiry_time },
        },
        projection={ 'locks': 1 },
        return_document=ReturnDocument.AFTER
    )
    if already_owned:
        item = LockableDocument.parse_obj(already_owned)
        lock = next(filter(lambda l: l.work_queue_id == work_queue.id and l.expires > now, item.locks))
        return TakeLockResponse(acquired_lock=True, lock=lock)

    # Check if anyone owns the lock, if no take it
    acquired = await Collection.get_motor_collection().find_one_and_update(
        {
            '_id': item_id,
            'locks': {
                '$not': {
                    '$elemMatch': {
                        'work_queue_id': work_queue.id,
                        'expires': { '$gt': now }
                    }
                }
            }
        },
        {
            '$addToSet': {
                'locks': {
                    'work_queue_id': work_queue.id,
                    'expires': expiry_time,
                    'user_id': current_user.id
                }
            },
        },
        projection={ 'locks': 1 },
        return_document=ReturnDocument.AFTER
    )
    if acquired:
        item = LockableDocument.parse_obj(acquired)
        lock = next(filter(lambda l: l.work_queue_id == work_queue.id and l.expires > now, item.locks))
        return TakeLockResponse(acquired_lock=True, lock=lock)

    item: LockableDocument | None = await Collection.find_one({ '_id': item_id }).project(LockableDocument)
    if not item:
        raise HTTPException(
            detail=f"{work_queue.collection_name} {item_id} Not Found", status_code=status.HTTP_404_NOT_FOUND
        )

    lock = next(filter(lambda l: l.work_queue_id == item_id and l.expires > now, item.locks))
    return TakeLockResponse(acquired_lock=False, lock=lock)

@router.post("/{id}/items/take-next", response_model=TakeNextWorkQueueResponse)
async def take_next_work_item(
    work_queue: WorkQueue = Depends(get_target),
    current_user: User = Security(get_current_user),
):
    Collection: Type[BaseDocument] = getattr(collection_classes, work_queue.collection_name)
    now = datetime.datetime.now()
    unclaimed_query = {
        'locks': {
            '$not': {
                '$elemMatch': {
                    'work_queue_id': work_queue.id,
                    'expires': { '$gt': now }
                }
            }
        }
    }
    for _ in range(5):
        item = await Collection.find(work_queue.document_query) \
                               .find(unclaimed_query) \
                               .sort(*work_queue.sort_query) \
                               .project(IdOnlyDocument) \
                               .first_or_none()
        if not item or not item.id:
            await asyncio.sleep(0.1)
            continue

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

@router.post("/{id}/items/{item_id}/submit", response_model=SubmitWorkItemResponse)
async def submit_work_item(
    body: SubmitWorkItemRequest,
    item_id: PydanticObjectId,
    logger: Logger = Depends(get_logger),
    work_queue: WorkQueue = Depends(get_target),
    current_user: User = Security(get_current_user),
):
    Collection: Type[BaseDocument] = getattr(collection_classes, work_queue.collection_name)

    lock = await attempt_lock_acquire(work_queue, item_id, current_user)
    if not lock.acquired_lock:
        return SubmitWorkItemResponse(success=False)

    item = await Collection.get(item_id)
    if not item:
        raise HTTPException(
            detail=f"{item_id} Not Found", status_code=status.HTTP_404_NOT_FOUND
        )
    action = next(filter(lambda a: a.label == body.action_label, work_queue.submit_actions))
    if action.reassignable and action.dest_queue and body.reassignment:
        dest_user = await User.get(body.reassignment)
        dest_queue = await WorkQueue.find_one(WorkQueue.name == action.dest_queue)
        if dest_queue and dest_user:
            expires = datetime.datetime.now() + datetime.timedelta(days=365)
            await attempt_lock_acquire(dest_queue, item_id, dest_user, expires)

    if body.comment:
        now = datetime.datetime.now()
        comment = Comment(
            target_id=item_id,
            user_id=current_user.id,  # type: ignore
            time=now,
            text=body.comment
        )
        await comment.save()

    await update_and_log_diff(logger, current_user, item, body.updates)
    await Collection.find_one({ '_id': item_id }).update({ '$pull': { 'locks': { 'work_queue_id': work_queue.id } } })

    return SubmitWorkItemResponse(success=True)
    