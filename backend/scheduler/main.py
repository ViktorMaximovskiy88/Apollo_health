import asyncio
from functools import cache
from pathlib import Path
import sys
from beanie import PydanticObjectId
import boto3
import typer

from datetime import datetime

sys.path.append(str(Path(__file__).parent.joinpath("../..").resolve()))

from backend.common.core.config import is_local
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

def find_sites_eligible_for_scraping(crons):
    sites = Site.find({
        'cron': { '$in': crons }, # Should be run now
        'disabled': False, # Is active
        'base_urls.status': 'ACTIVE', # has at least one active url
        'last_status': { '$nin': ['QUEUED', 'IN_PROGRESS', 'CANCELLING'] } # not already in progress
    })
    return sites

async def enqueue_scrape_task(site_id: PydanticObjectId):
    site_scrape_task = SiteScrapeTask(site_id=site_id, queued_time=datetime.now())

    update_result = await SiteScrapeTask.get_motor_collection().update_one(
        { 'site_id': site_id, 'status': { '$in': ['QUEUED', 'IN_PROGRESS', 'CANCELLING'] } },
        { '$setOnInsert': site_scrape_task.dict() },
        { 'upsert': True },
    )

    insert_id: PydanticObjectId | None = update_result.upserted_id  # type: ignore
    
    if not insert_id:
        return None

    site_scrape_task.id = insert_id
    return site_scrape_task

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
        crons = compute_matching_crons(datetime.now())
        sites = find_sites_eligible_for_scraping(crons)

        async for site in sites:
            site_id: PydanticObjectId = site.id # type: ignore
            site_scrape_task = await enqueue_scrape_task(site_id)
            if site_scrape_task:
                await log_task_creation(logger, user, site_scrape_task)
            
            await asyncio.sleep(1)

        await asyncio.sleep(5)

@cache
def cluster_arn() -> str:
    ecs = boto3.client("ecs")
    clusters = ecs.list_clusters()
    return clusters['clusterArns'][0]

@cache
def scrapeworker_service_arn() -> str:
    ecs = boto3.client("ecs")
    services = ecs.list_services(cluster=cluster_arn())
    arns = services['serviceArns']
    return next(filter(lambda arn: 'scrapeworker' in arn, arns))

def determine_current_instance_count(service_tag: str):
    ecs = boto3.client("ecs")
    services = ecs.describe_services(
        cluster=cluster_arn(),
        services=[scrapeworker_service_arn()]
    )
    return services['services'][0]['desiredCount']

def update_cluster_size(size: int | None):
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
        active_workers = determine_current_instance_count('scrapeworker')
        tasks_per_worker = 5 # some setting
        new_cluster_size = get_new_cluster_size(queue_size, active_workers, tasks_per_worker)
        update_cluster_size(new_cluster_size)
        await asyncio.sleep(30)

async def start_scheduler_and_scaler():
    await init_db()
    await asyncio.gather(start_scaler(), start_scheduler())

@app.command()
def start_worker():
    typer.secho(f"Starting Scheduler", fg=typer.colors.GREEN)
    asyncio.run(start_scheduler_and_scaler())


if __name__ == "__main__":
    app()
