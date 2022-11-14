from beanie import PydanticObjectId
from fastapi import APIRouter, Security

from backend.app.core.settings import settings
from backend.app.utils.user import get_current_user
from backend.common.models.lineage import LineageDoc
from backend.common.services.document import get_site_lineage
from backend.common.sqs.lineage_task import LineageTaskQueue

lineage_queue = LineageTaskQueue(
    queue_url=settings.lineage_worker_queue_url,
)

router = APIRouter(
    prefix="/lineage",
    tags=["Lineage"],
)


@router.get("/reprocess/{site_id}", dependencies=[Security(get_current_user)])
async def reprocess_lineage_for_site(site_id: PydanticObjectId):
    sqs_response, task = await lineage_queue.enqueue({"site_id": site_id, "reprocess": True})
    return task


@router.get(
    "/{site_id}", dependencies=[Security(get_current_user)], response_model=list[LineageDoc]
)
async def fetch_lineage_for_site(site_id: PydanticObjectId):
    docs = await get_site_lineage(site_id)
    return docs
