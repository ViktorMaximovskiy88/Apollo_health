import logging

from beanie import PydanticObjectId
from fastapi import APIRouter, BackgroundTasks, Security

from backend.app.utils.user import get_current_user
from backend.common.models.lineage import LineageDoc
from backend.common.services.document import get_site_lineage
from backend.common.services.lineage.core import LineageService

lineage_service = LineageService(logger=logging.getLogger("app"))
router = APIRouter(
    prefix="/lineage",
    tags=["Lineage"],
)


@router.get("/reprocess/{site_id}", dependencies=[Security(get_current_user)])
async def reprocess_lineage_for_site(
    site_id: PydanticObjectId,
    background_tasks: BackgroundTasks,
):
    await lineage_service.reprocess_lineage_for_site(site_id)
    background_tasks.add_task(lineage_service.reprocess_lineage_for_site, site_id)
    return {"message": "Lineage task queued"}


@router.get(
    "/{site_id}", dependencies=[Security(get_current_user)], response_model=list[LineageDoc]
)
async def fetch_lineage_for_site(site_id: PydanticObjectId):
    docs = await get_site_lineage(site_id)
    return docs
