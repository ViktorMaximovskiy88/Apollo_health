from datetime import datetime
from beanie import PydanticObjectId
from beanie.odm.operators.update.general import Set
from fastapi import APIRouter, Depends, HTTPException, status
from backend.common.models.site import Site

from backend.common.models.site_scrape_task import SiteScrapeTask, UpdateSiteScrapeTask
from backend.common.models.user import User
from backend.app.utils.logger import (
    Logger,
    create_and_log,
    get_logger,
    update_and_log_diff,
)
from backend.app.utils.user import get_current_user

router = APIRouter(
    prefix="/site-scrape-tasks",
    tags=["SiteScrapeTasks"],
)


async def get_target(id: PydanticObjectId):
    user = await SiteScrapeTask.get(id)
    if not user:
        raise HTTPException(
            detail=f"Site Scrape Task {id} Not Found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return user


@router.get("/", response_model=list[SiteScrapeTask])
async def read_scrape_tasks_for_site(
    site_id: PydanticObjectId,
    current_user: User = Depends(get_current_user),
):
    scrape_tasks: list[SiteScrapeTask] = (
        await SiteScrapeTask.find_many(SiteScrapeTask.site_id == site_id)
        .sort("-queued_time")
        .to_list()
    )
    return scrape_tasks


@router.get("/{id}", response_model=SiteScrapeTask)
async def read_scrape_task(
    target: User = Depends(get_target),
    current_user: User = Depends(get_current_user),
):
    return target


@router.put("/", response_model=SiteScrapeTask, status_code=status.HTTP_201_CREATED)
async def start_scrape_task(
    site_id: PydanticObjectId,
    current_user: User = Depends(get_current_user),
    logger: Logger = Depends(get_logger),
):
    site_scrape_task = SiteScrapeTask(site_id=site_id, queued_time=datetime.now())

    # NOTE: Could use a transaction here
    await create_and_log(logger, current_user, site_scrape_task)
    await Site.find_one(Site.id == site_id).update(
        Set({
            Site.last_status: site_scrape_task.status,
        })
    )
    return site_scrape_task


@router.post("/{id}", response_model=SiteScrapeTask)
async def update_scrape_task(
    updates: UpdateSiteScrapeTask,
    target: SiteScrapeTask = Depends(get_target),
    current_user: User = Depends(get_current_user),
    logger: Logger = Depends(get_logger),
):
    # NOTE: Could use a transaction here
    updated = await update_and_log_diff(logger, current_user, target, updates)
    await Site.find_one(Site.id == target.site_id).update(
        Set({Site.last_status: updates.status}),
    )
    return updated


@router.delete("/{id}")
async def delete_site_scrape_task(
    target: SiteScrapeTask = Depends(get_target),
    current_user: User = Depends(get_current_user),
    logger: Logger = Depends(get_logger),
):
    await update_and_log_diff(
        logger, current_user, target, UpdateSiteScrapeTask(disabled=True)
    )
    return {"success": True}
