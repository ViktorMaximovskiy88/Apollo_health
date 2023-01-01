from beanie import PydanticObjectId
from fastapi import APIRouter, BackgroundTasks, Security

import backend.common.models.tasks as tasks
from backend.app.core.settings import settings
from backend.app.utils.user import get_current_user
from backend.common.models.site import Site
from backend.common.models.user import User
from backend.common.tasks.task_queue import TaskQueue

task_queue = TaskQueue(
    queue_url=settings.task_worker_queue_url,
)


router = APIRouter(
    prefix="/task",
    tags=["Tasks"],
)


@router.get("/{task_id}", dependencies=[Security(get_current_user)], response_model=tasks.TaskLog)
async def get_task(
    task_id: PydanticObjectId,
) -> tasks.TaskLog:
    task: tasks.TaskLog = await tasks.TaskLog.get(task_id)
    return task


@router.get("/", response_model=list[tasks.TaskLog])
async def get_user_task(
    current_user: User = Security(get_current_user),
) -> list[tasks.TaskLog]:
    tasks: list[tasks.TaskLog] = await tasks.TaskLog.get_incomplete_for_user(current_user)
    return tasks


async def enqueue_site_tasks(task_type: str, current_user: User):
    TaskType = getattr(tasks, task_type)
    async for site in Site.find():
        print(site)
        task_payload = TaskType(site_id=site.id, reprocess=True)
        await task_queue.enqueue(task_payload, current_user.id)


@router.post("/reprocess/sites/{task_type}")
async def bulk_reprocess_site_task(
    task_type: str,
    background_tasks: BackgroundTasks,
    current_user: User = Security(get_current_user),
) -> tasks.TaskLog:
    background_tasks.add_task(enqueue_site_tasks, task_type, current_user)
    return {}


@router.post("/enqueue/{task_type}", response_model=tasks.TaskLog)
async def enquque_task(
    task_type: str,
    # TODO reconcile 'typing' between generics and pydantic
    payload: tasks.DocTask | tasks.SiteTask | tasks.PDFDiffTask,
    current_user: User = Security(get_current_user),
) -> tasks.TaskLog:
    TaskType = getattr(tasks, task_type)
    task_payload = TaskType(**payload.dict())
    task = await task_queue.enqueue(task_payload, current_user.id)
    return task
