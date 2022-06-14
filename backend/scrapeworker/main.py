import asyncio
from pathlib import Path
import sys
from uuid import uuid4
import traceback
import typer
import signal
from playwright.async_api import async_playwright

from datetime import datetime
import pymongo
from pymongo import ReturnDocument
from beanie.odm.operators.update.general import Set

sys.path.append(str(Path(__file__).parent.joinpath("../..").resolve()))
from backend.common.db.init import init_db
from backend.common.models.site import Site
from backend.common.models.site_scrape_task import SiteScrapeTask
from backend.scrapeworker.scrape_worker import ScrapeWorker, CancellationException

app = typer.Typer()

accepting_tasks = True


def signal_handler(signum, frame):
    global accepting_tasks
    typer.secho(f"Shutdown Requested, no longer accepting tasks", fg=typer.colors.BLUE)
    accepting_tasks = False


async def pull_task_from_queue(worker_id):
    now = datetime.now()
    acquired = await SiteScrapeTask.get_motor_collection().find_one_and_update(
        {"status": "QUEUED"},
        {
            "$set": {
                "start_time": now,
                "worker_id": worker_id,
                "status": "IN_PROGRESS",
            }
        },
        sort=[("queued_time", pymongo.ASCENDING)],
        return_document=ReturnDocument.AFTER,
    )
    if acquired:
        scrape_task = SiteScrapeTask.parse_obj(acquired)
        typer.secho(f"Acquired Task {scrape_task.id}", fg=typer.colors.BLUE)
        return scrape_task


async def log_success(scrape_task, site):
    typer.secho(f"Finished Task {scrape_task.id}", fg=typer.colors.BLUE)
    now = datetime.now()
    await site.update(Set({Site.last_status: "FINISHED", Site.last_run_time: now}))
    await scrape_task.update(
        Set(
            {
                SiteScrapeTask.status: "FINISHED",
                SiteScrapeTask.end_time: now,
            }
        )
    )


async def log_failure(scrape_task, site, ex):
    message = traceback.format_exc()
    traceback.print_exc()
    typer.secho(f"Task Failed {scrape_task.id}", fg=typer.colors.RED)
    now = datetime.now()
    await site.update(
        Set(
            {
                Site.last_status: "FAILED",
                Site.last_run_time: now,
            }
        )
    )
    await scrape_task.update(
        Set(
            {
                SiteScrapeTask.status: "FAILED",
                SiteScrapeTask.error_message: message,
                SiteScrapeTask.end_time: now,
            }
        )
    )


async def log_cancellation(scrape_task, site, ex):
    message = traceback.format_exc()
    traceback.print_exc()
    typer.secho(f"Task Canceled {scrape_task.id}", fg=typer.colors.RED)
    now = datetime.now()
    await site.update(
        Set(
            {
                Site.last_status: "CANCELED",
                Site.last_run_time: now,
            }
        )
    )
    await scrape_task.update(
        Set(
            {
                SiteScrapeTask.status: "CANCELED",
                SiteScrapeTask.error_message: message,
                SiteScrapeTask.end_time: now,
            }
        )
    )


async def heartbeat_task(scrape_task: SiteScrapeTask):
    while True:
        await scrape_task.update({SiteScrapeTask.last_active: datetime.now()})
        await asyncio.sleep(1)


async def worker_fn(worker_id, playwright, browser):
    while True:
        if not accepting_tasks:
            return

        scrape_task = await pull_task_from_queue(worker_id)
        if not scrape_task:
            await asyncio.sleep(5)
            continue

        site = await Site.get(scrape_task.site_id)
        if not site:
            raise Exception("Site not found")

        now = datetime.now()
        await site.update(
            Set({Site.last_status: "IN_PROGRESS", Site.last_run_time: now})
        )

        worker = ScrapeWorker(playwright, browser, scrape_task, site)
        try:
            task = asyncio.create_task(heartbeat_task(scrape_task))
            await worker.run_scrape()
            task.cancel()
            await log_success(scrape_task, site)
        except CancellationException as ex:
            await log_cancellation(scrape_task, site, ex)
        except Exception as ex:
            await log_failure(scrape_task, site, ex)


async def start_worker_async(worker_id):
    await init_db()
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch()

        workers = []
        for _ in range(5):
            workers.append(worker_fn(worker_id, playwright, browser))
        await asyncio.gather(*workers)
    typer.secho(f"Shutdown Complete", fg=typer.colors.BLUE)


@app.command()
def start_worker():
    worker_id = uuid4()
    signal.signal(signal.SIGTERM, signal_handler)
    typer.secho(f"Starting Scrape Worder {worker_id}", fg=typer.colors.GREEN)
    asyncio.run(start_worker_async(worker_id))


if __name__ == "__main__":
    app()
