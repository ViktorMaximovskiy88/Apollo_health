import logging

from beanie import PydanticObjectId
from fastapi import APIRouter, BackgroundTasks, Security

from backend.app.utils.user import get_current_user
from backend.common.services.lineage import LineageService

lineage_service = LineageService(logger=logging)
router = APIRouter(
    prefix="/lineage",
    tags=["Lineage"],
)


@router.get("/{site_id}", dependencies=[Security(get_current_user)])
async def lineage_for_site(
    site_id: PydanticObjectId,
    background_tasks: BackgroundTasks,
):
    background_tasks.add_task(lineage_service.process_lineage_for_site, site_id)
    return {"message": "Lineage task queued"}
