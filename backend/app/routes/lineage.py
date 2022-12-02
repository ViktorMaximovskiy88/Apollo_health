from beanie import PydanticObjectId
from fastapi import APIRouter, Security

from backend.app.core.settings import settings
from backend.app.utils.user import get_current_user
from backend.common.models.lineage import LineageDoc
from backend.common.models.tasks import LineageTask
from backend.common.models.user import User
from backend.common.services.document import get_site_lineage
from backend.common.tasks.task_queue import TaskQueue

task_queue = TaskQueue(
    queue_url=settings.task_worker_queue_url,
)

router = APIRouter(
    prefix="/lineage",
    tags=["Lineage"],
)


@router.post("/reprocess/{site_id}")
async def reprocess_lineage_for_site(
    site_id: PydanticObjectId,
    current_user: User = Security(get_current_user),
):
    task_payload = LineageTask(site_id=site_id, reprocess=True)
    task = await task_queue.enqueue(task_payload, created_by=current_user)
    return {"task": task}


@router.get(
    "/{site_id}", dependencies=[Security(get_current_user)], response_model=list[LineageDoc]
)
async def fetch_lineage_for_site(site_id: PydanticObjectId):
    docs = await get_site_lineage(site_id)
    return docs
