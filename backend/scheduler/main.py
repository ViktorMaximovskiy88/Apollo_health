import asyncio
from pathlib import Path
import signal
import sys
from beanie import PydanticObjectId
import boto3
import typer

from datetime import datetime, timedelta
from beanie.odm.operators.update.general import Set

sys.path.append(str(Path(__file__).parent.joinpath("../..").resolve()))

from backend.common.task_queues.unique_task_insert import try_queue_unique_task
from backend.common.core.config import is_local, config
from backend.common.models.user import User
from backend.common.models.site_scrape_task import SiteScrapeTask
from backend.app.utils.logger import Logger

from backend.common.db.init import init_db
from backend.common.models.site import Site

app = typer.Typer()


def compute_matching_crons(now: datetime):
    crons = []
    for minute in ['*', now.minute]:
        for hour in ['*', now.hour]:
            for day_of_month in ['*', now.day]:
                for month in ['*', now.month]:
                    for day_of_week in ['*', now.weekday()]:
                        # python has 0 as monday, cron has 0 as sunday
                        # prefer cron as that's the format we're using
                        if day_of_week != '*':
                            day_of_week = (day_of_week + 1) % 7
                        crons.append(f"{minute} {hour} {day_of_month} {month} {day_of_week}")
    return crons

async def get_schedule_user():
    user = await User.by_email("admin@mmitnetwork.com")
    if not user:
        raise Exception("No schedular found")
    return user

def find_sites_eligible_for_scraping(crons, now=datetime.now()):
    sites = Site.find({
        'cron': { '$in': crons }, # Should be run now
        'disabled': False, # Is active
        'base_urls.status': 'ACTIVE', # has at least one active url
        '$or': [
            { 'last_run_time': None }, # has never been run
            { 'last_run_time': { '$lt': now - timedelta(minutes=1) } }, # hasn't been run in the last minute
        ],
        'last_status': { '$nin': ['QUEUED', 'IN_PROGRESS', 'CANCELING'] } # not already in progress
    })
    return sites

async def enqueue_scrape_task(site_id: PydanticObjectId):
    site_scrape_task = SiteScrapeTask(site_id=site_id, queued_time=datetime.now())
    return await try_queue_unique_task(site_scrape_task)

async def log_task_creation(logger, user, site_scrape_task: SiteScrapeTask):
    await logger.background_log_change(user, site_scrape_task, "CREATE")
    await Site.find_one(Site.id == site_scrape_task.site_id).update(
        { '$set': { 'last_status': site_scrape_task.status } }
    )

async def start_scheduler():
    await init_db()
    logger = Logger()
    user = await get_schedule_user()
    while True:
        now = datetime.now()
        crons = compute_matching_crons(now)
        sites = find_sites_eligible_for_scraping(crons, now)

        async for site in sites:
            site_id: PydanticObjectId = site.id # type: ignore
            site_scrape_task = await enqueue_scrape_task(site_id)
            if site_scrape_task:
                await log_task_creation(logger, user, site_scrape_task)

            await asyncio.sleep(1)

        await asyncio.sleep(15)

def cluster_arn() -> str | None:
    return config.get('CLUSTER_ARN')

def scrapeworker_service_arn() -> str | None:
    return config.get('SCRAPEWORKER_SERVICE_ARN')

def determine_current_instance_count():
    ecs = boto3.client("ecs")
    services = ecs.describe_services(
        cluster=cluster_arn(),
        services=[scrapeworker_service_arn()]
    )
    return services['services'][0]['desiredCount']

def update_cluster_size(size: int | None):
    if size is None:
        return

    print("Settings cluster size to", size)

    ecs_client = boto3.client("ecs")
    response = ecs_client.update_service(
        cluster=cluster_arn(),
        service=scrapeworker_service_arn(),
        desiredCount=size,
    )
    print(response)


def get_new_cluster_size(queue_size, active_workers, tasks_per_worker):
    workers_needed = queue_size // tasks_per_worker

    if abs(workers_needed - active_workers) < 5:
        return None

    return max(workers_needed, 1) # never scale to zero

async def start_scaler():
    if is_local:
        typer.secho(f"Cannot run scaler locally", fg=typer.colors.RED)
        return

    while True:
        queue_size = await SiteScrapeTask.find(SiteScrapeTask.status == 'QUEUED').count()
        active_workers = determine_current_instance_count()
        tasks_per_worker = 5 # some setting
        new_cluster_size = get_new_cluster_size(queue_size, active_workers, tasks_per_worker)
        update_cluster_size(new_cluster_size)
        await asyncio.sleep(30)

async def start_hung_task_checker():
    """
    Fail tasks that are in progress but are not longer sending a heartbeat
    """
    while True:
        now = datetime.now()
        tasks = SiteScrapeTask.find({
            'status': { '$in': ['IN_PROGRESS', 'CANCELING'] },
            '$or': [
                { 'last_active': { '$lt': now - timedelta(minutes=5) } },
                { 'last_active': None }
            ],
        })
        message = "Lost task heartbeat"
        async for task in tasks:
            message = f"Failing task {task.id} on worker {task.worker_id} due to lost heartbeat"
            typer.secho(message, fg=typer.colors.RED)

            await Site.find(Site.id == task.site_id).update(
                Set(
                    {
                        Site.last_status: "FAILED",
                        Site.last_run_time: now,
                    }
                )
            )
            await task.update(
                Set(
                    {
                        SiteScrapeTask.status: "FAILED",
                        SiteScrapeTask.error_message: message,
                        SiteScrapeTask.end_time: now,
                    }
                )
            )
        await asyncio.sleep(60)

background_tasks: list[asyncio.Task] = []
async def start_scheduler_and_scaler():
    await init_db()
    background_tasks.append(asyncio.create_task(start_scaler()))
    background_tasks.append(asyncio.create_task(start_scheduler()))
    background_tasks.append(asyncio.create_task(start_hung_task_checker()))
    await asyncio.gather(*background_tasks)

def signal_handler(signum, frame):
    typer.secho(f"Shutdown Requested, shutting down", fg=typer.colors.BLUE)
    for task in background_tasks:
        task.cancel()

@app.command()
def start_worker():
    typer.secho(f"Starting Scheduler", fg=typer.colors.GREEN)
    signal.signal(signal.SIGTERM, signal_handler)
    asyncio.run(start_scheduler_and_scaler())


if __name__ == "__main__":
    app()
