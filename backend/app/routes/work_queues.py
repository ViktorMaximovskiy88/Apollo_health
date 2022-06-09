from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from backend.common.models.document_assessment import DocumentAssessment
from backend.common.models.user import User
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
    current_user: User = Depends(get_current_user),
):
    queues: list[WorkQueue] = await WorkQueue.find_many({}).to_list()
    return queues

@router.get("/counts")
async def read_document_assessments(
    current_user: User = Depends(get_current_user),
):
    response = []

    queues = WorkQueue.find_many({})
    async for queue in queues:
        count = await DocumentAssessment.find_many(queue.document_query).count()
        response.append({ 'work_queue_id': queue.id, 'count': count })

    return response

@router.get("/{id}", response_model=WorkQueue)
async def read_work_queue(
    target: WorkQueue = Depends(get_target),
    current_user: User = Depends(get_current_user),
):
    return target

@router.put("/", response_model=WorkQueue, status_code=status.HTTP_201_CREATED)
async def create_work_queue(
    work_queue: WorkQueue,
    current_user: User = Depends(get_current_user),
    logger: Logger = Depends(get_logger),
):
    new_queue = WorkQueue(
            name=work_queue.name,
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
    current_user: User = Depends(get_current_user),
    logger: Logger = Depends(get_logger),
):
    updated = await update_and_log_diff(logger, current_user, target, updates)
    return updated


@router.delete("/{id}")
async def delete_work_queue(
    target: WorkQueue = Depends(get_target),
    current_user: User = Depends(get_current_user),
    logger: Logger = Depends(get_logger),
):
    await update_and_log_diff(logger, current_user, target, WorkQueueUpdate(disabled=True))
    return {"success": True}
