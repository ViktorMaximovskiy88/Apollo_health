from datetime import datetime, timedelta, timezone

import typer
from beanie import PydanticObjectId
from beanie.odm.operators.update.general import Set
from fastapi import APIRouter, Depends, HTTPException, Security, status
from pymongo import ReturnDocument

from backend.app.routes.table_query import (
    TableFilterInfo,
    TableQueryResponse,
    TableSortInfo,
    get_query_json_list,
    query_table,
)
from backend.app.utils.logger import Logger, create_and_log, get_logger, update_and_log_diff
from backend.app.utils.user import get_current_user
from backend.common.core.enums import BulkScrapeActions, CollectionMethod, SiteStatus, TaskStatus
from backend.common.models.base_document import BaseModel
from backend.common.models.doc_document import DocDocument
from backend.common.models.document import RetrievedDocument
from backend.common.models.site import Site
from backend.common.models.site_scrape_task import SiteScrapeTask, UpdateSiteScrapeTask
from backend.common.models.user import User
from backend.common.task_queues.unique_task_insert import try_queue_unique_task

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
    response_model=TableQueryResponse,
    dependencies=[Security(get_current_user)],
)
async def read_scrape_tasks_for_site(
    site_id: PydanticObjectId,
    limit: int | None = None,
    skip: int | None = None,
    sorts: list[TableSortInfo] = Depends(get_query_json_list("sorts", TableSortInfo)),
    filters: list[TableFilterInfo] = Depends(get_query_json_list("filters", TableFilterInfo)),
):
    query = SiteScrapeTask.find_many(SiteScrapeTask.site_id == site_id)
    return await query_table(query, limit, skip, sorts, filters)


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
    if not site:
        raise HTTPException(
            detail=f"Site {site_id} Not Found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    site_scrape_task = await SiteScrapeTask.find_one(
        {"site_id": site_id, "status": {"$in": [TaskStatus.QUEUED, TaskStatus.IN_PROGRESS]}}
    )
    if site_scrape_task:
        raise HTTPException(
            detail=f"Scrapetask {site_scrape_task.id} is already queued or in progress.",
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
        )
    if site.collection_method == CollectionMethod.Manual:
        site_scrape_task = SiteScrapeTask(
            site_id=site_id,
            initiator_id=current_user.id,
            start_time=datetime.now(tz=timezone.utc),
            queued_time=datetime.now(tz=timezone.utc),
            status=TaskStatus.IN_PROGRESS,
            collection_method=CollectionMethod.Manual,
        )

        # get the latest active site_scrape_task id
        previous_scrape_task = await SiteScrapeTask.find_one(
            {"site_id": site_id}, sort=[("start_time", -1)]
        )
        if previous_scrape_task:
            site_scrape_task.documents_found = previous_scrape_task.documents_found
            site_scrape_task.retrieved_document_ids = previous_scrape_task.retrieved_document_ids

            await create_and_log(logger, current_user, site_scrape_task)
        else:
            await create_and_log(logger, current_user, site_scrape_task)

    else:
        site_scrape_task = SiteScrapeTask(
            site_id=site_id, queued_time=datetime.now(tz=timezone.utc)
        )

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


def build_bulk_sites_query(bulk_type: str):
    find_query = {
        "disabled": False,
        "base_urls": {"$exists": True, "$not": {"$size": 0}},
        "collection_method": {"$ne": CollectionMethod.Manual},
        "status": {"$ne": SiteStatus.INACTIVE},
    }
    update_query = {Site.last_run_status: TaskStatus.QUEUED}

    if bulk_type == "new":
        find_query["status"] = SiteStatus.NEW
    elif bulk_type == "failed":
        find_query["last_run_status"] = {"$in": [TaskStatus.FAILED, TaskStatus.CANCELED]}
    elif bulk_type == "canceled":
        find_query["last_run_status"] = TaskStatus.CANCELED
    elif bulk_type == "cancel-active":
        del find_query["status"]
        find_query["last_run_status"] = {"$in": [TaskStatus.QUEUED, TaskStatus.IN_PROGRESS]}
    elif bulk_type == "all":
        find_query["last_run_status"] = {"$nin": [TaskStatus.QUEUED, TaskStatus.IN_PROGRESS]}
    elif bulk_type == "hold-all":
        del find_query["status"]
        hold_ts = datetime.now(tz=timezone.utc) + timedelta(days=1)
        update_query = {Site.collection_hold: hold_ts}
    elif bulk_type == "cancel-hold-all":
        find_query = {"collection_hold": {"$ne": None}}
        update_query = {Site.collection_hold: None}

    return find_query, update_query


class BulkRunResponse(BaseModel):
    type: str
    scrapes: int | None = None
    sites: int | None = None


@router.post("/bulk-run", response_model=BulkRunResponse)
async def run_bulk_by_type(
    type: str,
    logger: Logger = Depends(get_logger),
    current_user: User = Security(get_current_user),
):
    async def cancel_site_scrapes(site_id: PydanticObjectId) -> int:
        query = {
            "site_id": site_id,
            "status": {"$in": [TaskStatus.QUEUED, TaskStatus.IN_PROGRESS]},
        }
        scrapes = SiteScrapeTask.find_many(query)
        scrapes_count = await scrapes.count()
        await scrapes.set({"status": TaskStatus.CANCELING})

        return scrapes_count

    bulk_type = type
    total_scrapes = 0
    total_sites = 0

    find_query, update_query = build_bulk_sites_query(bulk_type)
    sites = Site.find_many(find_query)
    if bulk_type == "cancel-hold-all":
        total_sites = await sites.count()
        await sites.set(update_query)
    else:
        async for site in sites:
            site_id: PydanticObjectId = site.id  # type: ignore
            update = {**update_query}

            if bulk_type == "cancel-active" or bulk_type == "hold-all":
                scrapes_canceled = await cancel_site_scrapes(site_id)
                total_scrapes += scrapes_canceled
                if scrapes_canceled > 0:
                    update[Site.last_run_status] = TaskStatus.CANCELING
            else:
                site_scrape_task = SiteScrapeTask(
                    site_id=site_id, queued_time=datetime.now(tz=timezone.utc)
                )
                queued_task = await try_queue_unique_task(site_scrape_task)
                if queued_task:
                    total_scrapes += 1
                    await logger.background_log_change(current_user, site_scrape_task, "CREATE")

            total_sites += 1
            await site.update(Set(update))

    res_type = BulkScrapeActions.RUN
    if bulk_type == "cancel-active":
        res_type = BulkScrapeActions.CANCEL
    elif bulk_type == "hold-all":
        res_type = BulkScrapeActions.HOLD
    elif bulk_type == "cancel-hold-all":
        res_type = BulkScrapeActions.CANCEL_HOLD

    return BulkRunResponse(type=res_type, sites=total_sites, scrapes=total_scrapes)


@router.post("/cancel-all", response_model=SiteScrapeTask)
async def cancel_all_site_scrape_task(
    site_id: PydanticObjectId,
    current_user: User = Depends(get_current_user),
):
    # fetch the site to determine the last_run_status is either QUEUED or IN_PROGRESS
    site = await Site.find_one(
        {
            "_id": site_id,
            "last_run_status": {
                "$in": [TaskStatus.QUEUED, TaskStatus.IN_PROGRESS, TaskStatus.FINISHED]
            },
        }
    )
    if site:
        if site.collection_method == CollectionMethod.Manual:
            last_site_task = await SiteScrapeTask.find_one(
                {
                    "site_id": site_id,
                    "status": {"$in": [TaskStatus.QUEUED, TaskStatus.IN_PROGRESS]},
                }
            )
            if last_site_task and last_site_task.documents_found == 0:
                await SiteScrapeTask.get_motor_collection().update_many(
                    {"site_id": site_id, "status": {"$in": [TaskStatus.IN_PROGRESS]}},
                    {"$set": {"status": TaskStatus.CANCELED}},
                )
                await site.update(Set({Site.last_run_status: TaskStatus.CANCELED}))
            else:
                await SiteScrapeTask.get_motor_collection().update_many(
                    {
                        "site_id": site_id,
                        "status": {"$in": [TaskStatus.QUEUED, TaskStatus.IN_PROGRESS]},
                    },
                    {"$set": {"status": TaskStatus.FINISHED}},
                )

                # change retrieve document if last_collected_date < today
                retrieved_documents: list[RetrievedDocument] = (
                    await RetrievedDocument.find_many(
                        {"_id": {"$in": last_site_task.retrieved_document_ids}}
                    )
                    .sort("-first_collected_date")
                    .to_list()
                )
                for r_doc in retrieved_documents:
                    if datetime.date(r_doc.last_collected_date) < datetime.today().date():
                        await RetrievedDocument.get_motor_collection().find_one_and_update(
                            {"_id": r_doc.id},
                            {"$set": {"last_collected_date": datetime.now(tz=timezone.utc)}},
                        )
                        await DocDocument.get_motor_collection().find_one_and_update(
                            {"retrieved_document_id": r_doc.id},
                            {"$set": {"last_collected_date": datetime.now(tz=timezone.utc)}},
                        )

                await site.update(Set({Site.last_run_status: TaskStatus.FINISHED}))
        else:
            # If the site is found, fetch all tasks and cancel all queued or in progress tasks
            await SiteScrapeTask.get_motor_collection().update_many(
                {
                    "site_id": site_id,
                    "status": {"$in": [TaskStatus.QUEUED, TaskStatus.IN_PROGRESS]},
                },
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
    responses={
        406: {"description": "Scrape task is not queued or in progress."},
    },
)
async def cancel_scrape_task(
    target: SiteScrapeTask = Depends(get_target),
):
    site = await Site.get(target.site_id)
    canceled_queued_task = await SiteScrapeTask.get_motor_collection().find_one_and_update(
        {"_id": target.id, "status": TaskStatus.QUEUED},
        {"$set": {"status": TaskStatus.CANCELED}},
        return_document=ReturnDocument.AFTER,
    )
    if canceled_queued_task:
        scrape_task = SiteScrapeTask.parse_obj(canceled_queued_task)
        typer.secho(f"Canceled Task {scrape_task.id} ", fg=typer.colors.BLUE)
        if site:
            await site.update(Set({Site.last_run_status: TaskStatus.CANCELED}))
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
        if site:
            await site.update(Set({Site.last_run_status: TaskStatus.CANCELING}))
        return scrape_task

    raise HTTPException(
        status_code=status.HTTP_406_NOT_ACCEPTABLE,
        detail="Scrape task is not queued or in progress.",
    )
