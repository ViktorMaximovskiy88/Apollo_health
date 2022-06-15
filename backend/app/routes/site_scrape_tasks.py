from datetime import datetime
from beanie import PydanticObjectId
from beanie.odm.operators.update.general import Set
from fastapi import APIRouter, Depends, HTTPException, status
import pymongo
from pymongo import ReturnDocument
import typer

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
        Set(
            {
                Site.last_status: site_scrape_task.status,
            }
        )
    )
    return site_scrape_task


@router.post("/bulk-run")
async def runBulkByType(
    type: str,
    logger: Logger = Depends(get_logger),
    current_user: User = Depends(get_current_user),
):
    bulk_type = type
    total_scrapes = 0
    query = {"disabled": False, "base_urls": {"$exists": True, "$not": {"$size": 0}}}
    if bulk_type == "unrun":
        query["last_status"] = None
    elif bulk_type == "failed":
        query["last_status"] = "FAILED"
    elif bulk_type == "all":
        query["last_status"] = {"$ne": ["QUEUED", "IN_PROGRESS"]}

    async for site in Site.find_many(query):
        site_id: PydanticObjectId = site.id # type: ignore
        site_scrape_task = SiteScrapeTask(site_id=site_id, queued_time=datetime.now())
        update_result = await SiteScrapeTask.get_motor_collection().update_one(
            {
                "site_id": site.id,
                "status": {"$in": ["QUEUED", "IN_PROGRESS", "CANCELLING"]},
            },
            {"$setOnInsert": site_scrape_task.dict()},
            upsert=True,
        )

        insert_id: PydanticObjectId | None = update_result.upserted_id  # type: ignore
        if insert_id:
            site_scrape_task.id = insert_id
            total_scrapes += 1
            await logger.background_log_change(current_user, site_scrape_task, "CREATE")
            await Site.find_one(Site.id == site.id).update(
                Set(
                    {
                        Site.last_status: site_scrape_task.status,
                    }
                )
            )

    return {"status": True, "scrapes_launched": total_scrapes}


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


@router.post("/{id}/cancel", response_model=SiteScrapeTask)
async def cancel_scrape_task(
    target: SiteScrapeTask = Depends(get_target),
    current_user: User = Depends(get_current_user),
):
    canceled_queued_task = (
        await SiteScrapeTask.get_motor_collection().find_one_and_update(
            {"_id": target.id, "status": "QUEUED"},
            {"$set": {"status": "CANCELED"}},
            return_document=ReturnDocument.AFTER,
        )
    )
    if canceled_queued_task:
        scrape_task = SiteScrapeTask.parse_obj(canceled_queued_task)
        typer.secho(f"Canceled Task {scrape_task.id} ", fg=typer.colors.BLUE)
        return scrape_task

    acquired = await SiteScrapeTask.get_motor_collection().find_one_and_update(
        {"_id": target.id, "status": "IN_PROGRESS"},
        {
            "$set": {
                "status": "CANCELING",
            }
        },
        return_document=ReturnDocument.AFTER,
    )
    if acquired:
        scrape_task = SiteScrapeTask.parse_obj(acquired)
        typer.secho(f"Set Task {scrape_task.id} 'Canceling'", fg=typer.colors.BLUE)
        return scrape_task
