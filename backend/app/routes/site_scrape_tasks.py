from datetime import datetime
from beanie import PydanticObjectId
from beanie.odm.operators.update.general import Set
from fastapi import APIRouter, Depends, HTTPException, status, Security
import pymongo
from pymongo import ReturnDocument
import typer

from backend.common.models.site import Site
from backend.common.models.site_scrape_task import SiteScrapeTask, UpdateSiteScrapeTask
from backend.common.models.user import User
from backend.common.core.enums import TaskStatus
from backend.app.utils.logger import (
    Logger,
    create_and_log,
    get_logger,
    update_and_log_diff,
)
from backend.app.utils.user import get_current_user
from backend.common.task_queues.unique_task_insert import try_queue_unique_task
from backend.common.core.enums import CollectionMethod

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


@router.get(
    "/",
    response_model=list[SiteScrapeTask],
    dependencies=[Security(get_current_user)],
)
async def read_scrape_tasks_for_site(
    site_id: PydanticObjectId,
):
    scrape_tasks: list[SiteScrapeTask] = (
        await SiteScrapeTask.find_many(SiteScrapeTask.site_id == site_id)
        .sort("-queued_time")
        .to_list()
    )
    return scrape_tasks


@router.get(
    "/{id}",
    response_model=SiteScrapeTask,
    dependencies=[Security(get_current_user)],
)
async def read_scrape_task(
    target: User = Depends(get_target),
):
    return target


@router.put(
    "/",
    response_model=SiteScrapeTask,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Security(get_current_user)],
)
async def start_scrape_task(
    site_id: PydanticObjectId,
    current_user: User = Security(get_current_user),
    logger: Logger = Depends(get_logger),
):
    site = await Site.get(site_id)
    site_scrape_task = None;
    if site.collection_method == CollectionMethod.Manual:
        site_scrape_task = SiteScrapeTask(
            site_id=site_id, 
            start_time=datetime.now(), 
            queued_time=datetime.now(), 
            status=TaskStatus.IN_PROGRESS, 
            collection_type=CollectionMethod.Manual
        )
    else:
        site_scrape_task = SiteScrapeTask(site_id=site_id, queued_time=datetime.now())

    # NOTE: Could use a transaction here
    await create_and_log(logger, current_user, site_scrape_task)
    await site.update(
        Set(
            {
                Site.last_run_status: site_scrape_task.status,
            }
        )
    )
    return site_scrape_task


@router.post("/bulk-run")
async def runBulkByType(
    type: str,
    logger: Logger = Depends(get_logger),
    current_user: User = Security(get_current_user),
):
    bulk_type = type
    total_scrapes = 0
    query = {
        "disabled": False,
        "base_urls": {"$exists": True, "$not": {"$size": 0}},
        "collection_method": {"$ne": [CollectionMethod.Manual]},
    }
    if bulk_type == "unrun":
        query["last_run_status"] = None
    elif bulk_type == "failed":
        query["last_run_status"] = {"$ne": [TaskStatus.FAILED, TaskStatus.CANCELED]}
    elif bulk_type == "canceled":
        query["last_run_status"] = TaskStatus.CANCELED
    elif bulk_type == "cancel-active":
       query["last_run_status"] = {"$in": [TaskStatus.QUEUED, TaskStatus.IN_PROGRESS]}
    elif bulk_type == "all":
        query["last_run_status"] = {"$ne": [TaskStatus.QUEUED, TaskStatus.IN_PROGRESS]}

    async for site in Site.find_many(query):
        site_id: PydanticObjectId = site.id

        if bulk_type == "cancel-active":
            total_scrapes += 1
            result = await SiteScrapeTask.get_motor_collection().update_many(
                {"site_id": site_id, "status":{ "$in": [ TaskStatus.QUEUED, TaskStatus.IN_PROGRESS ] }},
                {"$set": {"status": TaskStatus.CANCELING}}
            )
            await site.update(
                Set(
                    {
                        Site.last_run_status: TaskStatus.CANCELING

                    }
                )
            )
        else:
            site_scrape_task = SiteScrapeTask(
                site_id=site_id, queued_time=datetime.now())
            site_scrape_task = await try_queue_unique_task(site_scrape_task)
            if site_scrape_task:
                total_scrapes += 1
                await logger.background_log_change(current_user, site_scrape_task, "CREATE")
                await Site.find_one(Site.id == site.id).update(
                    Set(
                        {
                            Site.last_run_status: site_scrape_task.status,
                        }
                    )
                )

    if bulk_type == "cancel-active":
        return {"status": True, "canceled_srapes": total_scrapes}
    else:
         return {"status": True, "scrapes_launched": total_scrapes}


@router.post("/cancel-all", response_model=SiteScrapeTask)
async def cancel_all_site_scrape_task(
    site_id: PydanticObjectId,
    current_user: User = Depends(get_current_user),
):
    # fetch the site to determine the last_run_status is either QUEUED or IN_PROGRESS
    site = await Site.find_one({"_id": site_id, "last_run_status": {"$in": [TaskStatus.QUEUED, TaskStatus.IN_PROGRESS]}})
    if site:
        if site.collection_method == CollectionMethod.Manual:

            last_site_task = await SiteScrapeTask.find_one({"site_id": site_id, "status":{ "$in": [ TaskStatus.QUEUED, TaskStatus.IN_PROGRESS ] }})

            if last_site_task.documents_found == 0:
                result = await SiteScrapeTask.get_motor_collection().update_many(
                    {"site_id": site_id, "status": {"$in": [TaskStatus.IN_PROGRESS]}},
                    {"$set": {"status": TaskStatus.CANCELED}},
                )
                await site.update(Set({Site.last_run_status: TaskStatus.CANCELED}))
            else:
                result = await SiteScrapeTask.get_motor_collection().update_many(
                    {"site_id": site_id, "status": {"$in": [TaskStatus.QUEUED, TaskStatus.IN_PROGRESS]}},
                    {"$set": {"status": TaskStatus.FINISHED}},
                )
                await site.update(Set({Site.last_run_status: TaskStatus.FINISHED}))
        else:
            # If the site is found, fetch all tasks and cancel all queued or in progress tasks
            result = await SiteScrapeTask.get_motor_collection().update_many(
                {"site_id": site_id, "status": {"$in": [TaskStatus.QUEUED, TaskStatus.IN_PROGRESS]}},
                {"$set": {"status": TaskStatus.CANCELING}},
            )
            await site.update(Set({Site.last_run_status: TaskStatus.CANCELING}))


@router.post("/{id}", response_model=SiteScrapeTask)
async def update_scrape_task(
    updates: UpdateSiteScrapeTask,
    target: SiteScrapeTask = Depends(get_target),
    current_user: User = Security(get_current_user),
    logger: Logger = Depends(get_logger),
):
    # NOTE: Could use a transaction here
    updated = await update_and_log_diff(logger, current_user, target, updates)
    await Site.find_one(Site.id == target.site_id).update(
        Set({Site.last_run_status: updates.status}),
    )
    return updated


@router.post(
    "/{id}/cancel",
    response_model=SiteScrapeTask,
    dependencies=[Security(get_current_user)],
)
async def cancel_scrape_task(
    target: SiteScrapeTask = Depends(get_target),
):
    canceled_queued_task = (
        await SiteScrapeTask.get_motor_collection().find_one_and_update(
            {"_id": target.id, "status": TaskStatus.QUEUED},
            {"$set": {"status": TaskStatus.CANCELED}},
            return_document=ReturnDocument.AFTER,
        )
    )
    if canceled_queued_task:
        scrape_task = SiteScrapeTask.parse_obj(canceled_queued_task)
        typer.secho(f"Canceled Task {scrape_task.id} ", fg=typer.colors.BLUE)
        return scrape_task

    acquired = await SiteScrapeTask.get_motor_collection().find_one_and_update(
        {"_id": target.id, "status": TaskStatus.IN_PROGRESS},
        {
            "$set": {
                "status": TaskStatus.CANCELING,
            }
        },
        return_document=ReturnDocument.AFTER,
    )
    if acquired:
        scrape_task = SiteScrapeTask.parse_obj(acquired)
        typer.secho(f"Set Task {scrape_task.id} 'Canceling'", fg=typer.colors.BLUE)
        return scrape_task
