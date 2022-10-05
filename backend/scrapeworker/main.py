from pathlib import Path

import newrelic.agent

newrelic.agent.initialize(Path(__file__).parent / "newrelic.ini")

import asyncio
import logging
import signal
import sys
from datetime import datetime, timezone
from uuid import UUID, uuid4

import pymongo
import typer
from beanie import PydanticObjectId
from beanie.odm.operators.update.general import Set
from playwright.async_api import Playwright, async_playwright
from pymongo import ReturnDocument

sys.path.append(str(Path(__file__).parent.joinpath("../..").resolve()))
from backend.common.core.enums import CollectionMethod, TaskStatus
from backend.common.db.init import init_db
from backend.common.models.site import Site
from backend.common.models.site_scrape_task import SiteScrapeTask
from backend.scrapeworker.common.exceptions import CanceledTaskException, NoDocsCollectedException
from backend.scrapeworker.log import log_cancellation, log_failure, log_not_found, log_success
from backend.scrapeworker.scrape_worker import ScrapeWorker

app = typer.Typer()
log = logging.getLogger(__name__)

accepting_tasks = True
active_tasks: dict[PydanticObjectId | None, SiteScrapeTask] = {}


async def signal_handler():
    global accepting_tasks, active_tasks
    typer.secho("Shutdown Requested, no longer accepting tasks", fg=typer.colors.BLUE)
    accepting_tasks = False
    for task in active_tasks.values():
        await task.update(Set({SiteScrapeTask.retry_if_lost: True}))


async def pull_task_from_queue(worker_id):
    now = datetime.now(tz=timezone.utc)
    acquired = await SiteScrapeTask.get_motor_collection().find_one_and_update(
        {"status": TaskStatus.QUEUED, "collection_method": CollectionMethod.Automated},
        {
            "$set": {
                "start_time": now,
                "last_active": now,
                "worker_id": worker_id,
                "status": TaskStatus.IN_PROGRESS,
            }
        },
        sort=[("queued_time", pymongo.ASCENDING)],
        return_document=ReturnDocument.AFTER,
    )
    if acquired:
        scrape_task = SiteScrapeTask.parse_obj(acquired)
        typer.secho(f"Acquired Task {scrape_task.id}", fg=typer.colors.BLUE)
        return scrape_task


async def heartbeat_task(scrape_task: SiteScrapeTask):
    while True:
        await SiteScrapeTask.get_motor_collection().update_one(
            {"_id": scrape_task.id}, {"$set": {"last_active": datetime.now(tz=timezone.utc)}}
        )
        await asyncio.sleep(10)


async def worker_fn(
    worker_id: UUID,
    playwright: Playwright,
):
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

        now = datetime.now(tz=timezone.utc)
        await site.update(
            Set(
                {
                    Site.last_run_status: TaskStatus.IN_PROGRESS,
                    Site.last_run_time: now,
                }
            )
        )

        browser = await playwright.chromium.launch(channel="chrome")
        worker = ScrapeWorker(playwright, browser, scrape_task, site)
        task = asyncio.create_task(heartbeat_task(scrape_task))
        active_tasks[scrape_task.id] = scrape_task
        try:
            await worker.run_scrape()
            await log_success(scrape_task, site)
        except CanceledTaskException as ex:
            await log_cancellation(scrape_task, site, ex)
        except NoDocsCollectedException as ex:
            await log_not_found(scrape_task, site, ex)
        except Exception as ex:
            await log_failure(scrape_task, site, ex)
        finally:
            del active_tasks[scrape_task.id]
            await browser.close()
            task.cancel()


async def start_worker_async(worker_id):
    await init_db()

    loop = asyncio.get_event_loop()
    loop.add_signal_handler(signal.SIGTERM, lambda: asyncio.create_task(signal_handler()))

    async with async_playwright() as playwright:
        workers = []
        for _ in range(1):
            workers.append(worker_fn(worker_id, playwright))
        await asyncio.gather(*workers)
    typer.secho("Shutdown Complete", fg=typer.colors.BLUE)


@app.command()
@newrelic.agent.background_task()
def start_worker():
    worker_id = uuid4()
    typer.secho(f"Starting Scrape Worker {worker_id}", fg=typer.colors.GREEN)
    asyncio.run(start_worker_async(worker_id))


if __name__ == "__main__":
    app()
