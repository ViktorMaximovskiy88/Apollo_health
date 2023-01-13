from pathlib import Path

import newrelic.agent

import backend.common.models as collection_classes
from backend.common.models.base_document import BaseDocument
from backend.common.models.work_queue import WorkQueue, WorkQueueMetric

newrelic.agent.initialize(Path(__file__).parent / "newrelic.ini")

import asyncio
import logging
import signal
import sys
from datetime import datetime, timedelta, timezone

import boto3
import typer
from beanie import PydanticObjectId
from beanie.odm.queries.find import FindMany

sys.path.append(str(Path(__file__).parent.joinpath("../..").resolve()))

from backend.app.core.settings import settings
from backend.app.utils.logger import Logger
from backend.common.core.config import config, is_local
from backend.common.core.enums import CollectionMethod, SiteStatus, TaskStatus
from backend.common.db.init import init_db
from backend.common.models.site import Site
from backend.common.models.site_scrape_task import SiteScrapeTask
from backend.common.models.user import User
from backend.common.task_queues.unique_task_insert import try_queue_unique_task

app = typer.Typer()


def compute_matching_crons(now: datetime):
    crons = []
    for minute in ["*", now.minute]:
        for hour in ["*", now.hour]:
            for day_of_month in ["*", now.day]:
                for month in ["*", now.month]:
                    for day_of_week in ["*", now.weekday()]:
                        # python has 0 as monday, cron has 0 as sunday
                        # prefer cron as that's the format we're using
                        if day_of_week != "*":
                            day_of_week = (day_of_week + 1) % 7
                        crons.append(f"{minute} {hour} {day_of_month} {month} {day_of_week}")
    return crons


async def get_schedule_user():
    user = await User.by_email("scheduler@mmitnetwork.com")
    if not user:
        raise Exception("No schedular found")
    return user


def find_sites_eligible_for_scraping(crons, now=datetime.now(tz=timezone.utc)):
    sites = Site.find(
        {
            "cron": {"$in": crons},  # Should be run now
            "disabled": False,  # Is active
            "status": {"$in": [SiteStatus.NEW, SiteStatus.QUALITY_HOLD, SiteStatus.ONLINE]},
            "collection_method": {"$ne": CollectionMethod.Manual},  # Isn't set to manual
            "base_urls.status": "ACTIVE",  # has at least one active url
            "$and": [
                {
                    "$or": [
                        {"last_run_time": None},  # has never been run
                        {
                            "last_run_time": {"$lt": now - timedelta(minutes=1)}
                        },  # hasn't been run in the last minute
                    ]
                },
                {
                    "$or": [
                        {"collection_hold": None},  # has no hold
                        {"collection_hold": {"$lt": now}},  # hold has expired
                    ]
                },
            ],
            "last_run_status": {
                "$nin": [
                    TaskStatus.QUEUED,
                    TaskStatus.IN_PROGRESS,
                    TaskStatus.CANCELING,
                ]  # not already in progress
            },
        }
    )
    return sites


async def enqueue_scrape_task(site_id: PydanticObjectId):
    site_scrape_task = SiteScrapeTask(site_id=site_id, queued_time=datetime.now(tz=timezone.utc))
    return await try_queue_unique_task(site_scrape_task)


async def log_task_creation(logger, user, site_scrape_task: SiteScrapeTask):
    await logger.background_log_change(user, site_scrape_task, "CREATE")
    await Site.find_one(Site.id == site_scrape_task.site_id).update(
        {"$set": {"last_run_status": site_scrape_task.status}}
    )


async def start_scheduler():
    if settings.disable_scrape_scheduling:
        typer.secho("Scrapes will not be automatically scheduled", fg=typer.colors.RED)
        return

    logger = Logger()
    user = await get_schedule_user()
    while True:
        now = datetime.now(tz=timezone.utc)
        crons = compute_matching_crons(now)
        sites = find_sites_eligible_for_scraping(crons, now)

        async for site in sites:
            logging.info(f"Queuing site {site.id} at {now}")
            site_id: PydanticObjectId = site.id  # type: ignore
            site_scrape_task = await enqueue_scrape_task(site_id)
            if site_scrape_task:
                await log_task_creation(logger, user, site_scrape_task)

            await asyncio.sleep(1)

        await asyncio.sleep(15)


def cluster_arn() -> str | None:
    return config.get("CLUSTER_ARN")


def scrapeworker_service_arn() -> str | None:
    return config.get("SCRAPEWORKER_SERVICE_ARN")


def get_worker_arns() -> set[str]:
    ecs = boto3.client("ecs")
    arns = []
    token = None
    while True:
        if token:
            response = ecs.list_tasks(
                cluster=cluster_arn(), serviceName="sourcehub-scrapeworker", nextToken=token
            )
        else:
            response = ecs.list_tasks(cluster=cluster_arn(), serviceName="sourcehub-scrapeworker")
        task_arns = response["taskArns"]
        describe_response = ecs.describe_tasks(cluster=cluster_arn(), tasks=task_arns)
        for task in describe_response["tasks"]:
            created_at = task["createdAt"]
            now = datetime.now(tz=timezone.utc)
            # Ignore recently launched tasks to avoid faling the deploy by immediately killing tasks
            if now - created_at > timedelta(minutes=10):
                arns.append(task["taskArn"])

        token = response.get("nextToken")
        if not token:
            return set(arns)


def tasks_of_status(*statuses: TaskStatus) -> FindMany[SiteScrapeTask]:
    return SiteScrapeTask.find(
        {
            "status": {"$in": list(statuses)},
            "collection_method": {"$ne": CollectionMethod.Manual},  # Isn't set to manual
        },
    )


async def identify_idle_workers(worker_arns: set[str]) -> list[str]:
    active_worker_arns = set()
    active_tasks = tasks_of_status(TaskStatus.IN_PROGRESS, TaskStatus.CANCELING)
    async for active_task in active_tasks:
        if active_task.task_arn in worker_arns:
            active_worker_arns.add(active_task.task_arn)
    return list(worker_arns - active_worker_arns)


async def get_surplus_worker_arns(worker_arns: set[str], workers_needed: int):
    worker_surplus = len(worker_arns) - workers_needed
    if worker_surplus <= 0:
        return []

    idle_workers = await identify_idle_workers(worker_arns)
    return idle_workers[:worker_surplus]


async def start_scaler():
    if is_local:
        typer.secho("Cannot run scaler locally", fg=typer.colors.RED)
        return

    while True:
        workers_needed = (
            await tasks_of_status(
                TaskStatus.QUEUED, TaskStatus.IN_PROGRESS, TaskStatus.CANCELING
            ).count()
            + 2
        )
        workers_needed = min(workers_needed, 100)

        ecs = boto3.client("ecs")
        worker_arns = get_worker_arns()
        for worker_arn in await get_surplus_worker_arns(worker_arns, workers_needed):
            ecs.stop_task(cluster=cluster_arn(), task=worker_arn)

        ecs.update_service(
            cluster=cluster_arn(), service=scrapeworker_service_arn(), desiredCount=workers_needed
        )

        await asyncio.sleep(30)


async def requeue_lost_task(task: SiteScrapeTask, now):
    message = f"Requeuing task {task.id} from worker {task.task_arn}, likely lost to killed worker"
    typer.secho(message, fg=typer.colors.RED)
    new_task = SiteScrapeTask(
        id=task.id,
        site_id=task.site_id,
        queued_time=now,
        scrape_method_configuration=task.scrape_method_configuration,
    )
    await new_task.save()
    await Site.find_one(Site.id == task.site_id).update({"$set": {"last_run_status": task.status}})


async def get_hung_tasks(now: datetime):
    tasks = SiteScrapeTask.find(
        {
            "status": {"$in": [TaskStatus.IN_PROGRESS, TaskStatus.CANCELING]},
            "collection_method": {"$ne": CollectionMethod.Manual},  # Isn't set to manual
            "$or": [
                {"last_active": {"$lt": now - timedelta(minutes=5)}},
                {"last_active": None},
            ],
        }
    )
    async for task in tasks:
        site = await Site.get(task.site_id)
        if site and site.collection_hold:
            if site.collection_hold.replace(tzinfo=timezone.utc) > now:
                logging.info(f"Site {site.id} held, skipping requeue.")
                continue
        yield task


def stop_task_worker(task: SiteScrapeTask):
    if not task.task_arn:  # nothing to stop
        return

    ecs = boto3.client("ecs")
    # Ignore errors when task does not exist or is already stopped
    try:
        ecs.stop_task(task=task.task_arn)
    except Exception:
        pass


async def start_hung_task_checker():
    """
    Retry tasks that are in progress but are no longer sending a heartbeat
    """
    while True:
        now = datetime.now(tz=timezone.utc)
        async for task in get_hung_tasks(now):
            if task.status == TaskStatus.IN_PROGRESS:
                await requeue_lost_task(task, now)
            elif task.status == TaskStatus.CANCELING:
                await task.update({"$set": {"status": TaskStatus.CANCELED}})
                await Site.find_one(Site.id == task.site_id).update(
                    {"$set": {"last_run_status": TaskStatus.CANCELED}}
                )
            # Always kill the worker because either the worker is already dead or in a bad state
            stop_task_worker(task)

        await asyncio.sleep(60)


async def start_work_queue_metrics():
    while True:
        if datetime.now(tz=timezone.utc).minute != 0:
            await asyncio.sleep(60)
            continue

        queues = WorkQueue.find_many({})
        async for work_queue in queues:
            Collection: BaseDocument = getattr(collection_classes, work_queue.collection_name)
            count, l_count, h_count, c_count = await asyncio.gather(
                Collection.find(work_queue.document_query).count(),
                Collection.find(work_queue.document_query | {"priority": {"$eq": 1}}).count(),
                Collection.find(work_queue.document_query | {"priority": {"$eq": 2}}).count(),
                Collection.find(work_queue.document_query | {"priority": {"$eq": 3}}).count(),
            )
            await WorkQueueMetric(
                queue_name=work_queue.name,
                total_count=count,
                low_priority_count=l_count,
                high_priority_count=h_count,
                critical_priority_count=c_count,
                time=datetime.now(tz=timezone.utc),
            ).save()

        await asyncio.sleep(60)


async def start_inactive_task_checker():
    """
    Cancel tasks where last document was scraped more than 1 hour ago
    """
    while True:
        now = datetime.now(tz=timezone.utc)
        scrape_task_query = SiteScrapeTask.find(
            {
                "status": {"$in": [TaskStatus.IN_PROGRESS]},
                "last_doc_collected": {"$lt": now - timedelta(hours=1)},
            }
        )
        async for task in scrape_task_query:
            await task.update(
                {
                    "$set": {
                        "status": TaskStatus.CANCELED,
                        "error_message": "Canceled due to inactivity",
                        "end_time": now,
                    }
                }
            )
            await Site.find_one(Site.id == task.site_id).update(
                {"$set": {"last_run_status": TaskStatus.CANCELED}}
            )
            # Always kill the worker because it doesn't know we have killed the task
            # so it won't pick up new tasks anyway, easiest to kill and boot a new worker
            stop_task_worker(task)

        await asyncio.sleep(60)


background_tasks: list[asyncio.Task] = []


async def start_scheduler_and_scaler():
    await init_db()
    background_tasks.append(asyncio.create_task(start_scaler()))
    background_tasks.append(asyncio.create_task(start_scheduler()))
    background_tasks.append(asyncio.create_task(start_hung_task_checker()))
    background_tasks.append(asyncio.create_task(start_inactive_task_checker()))
    background_tasks.append(asyncio.create_task(start_work_queue_metrics()))
    await asyncio.gather(*background_tasks)


def signal_handler(signum, frame):
    typer.secho("Shutdown Requested, shutting down", fg=typer.colors.BLUE)
    for task in background_tasks:
        task.cancel()


@app.command()
def start_worker():
    typer.secho("Starting Scheduler", fg=typer.colors.GREEN)
    signal.signal(signal.SIGTERM, signal_handler)
    asyncio.run(start_scheduler_and_scaler())


if __name__ == "__main__":
    app()
