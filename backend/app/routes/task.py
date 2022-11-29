from beanie import PydanticObjectId
from fastapi import APIRouter, Security

from backend.app.utils.user import get_current_user
from backend.common.models.tasks import TaskLog
from backend.common.models.user import User

router = APIRouter(
    prefix="/task",
    tags=["Tasks"],
)


@router.get("/{task_id}", dependencies=[Security(get_current_user)], response_model=TaskLog)
async def get_task(task_id: PydanticObjectId) -> TaskLog:
    task: TaskLog = await TaskLog.get(task_id)
    return task


@router.get("/", response_model=list[TaskLog])
async def get_user_task(current_user: User = Security(get_current_user)) -> list[TaskLog]:
    tasks: list[TaskLog] = await TaskLog.get_incomplete_for_user(current_user)
    return tasks
