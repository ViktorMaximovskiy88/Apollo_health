import asyncio
from pathlib import Path
import sys
from uuid import uuid4
import typer

from datetime import datetime
import pymongo
from pymongo import ReturnDocument
from beanie.odm.operators.update.general import Set

sys.path.append(str(Path(__file__).parent.joinpath("../..").resolve()))
from backend.common.db.init import init_db
from backend.common.models.site import Site
from backend.common.models.site_scrape_task import SiteScrapeTask
from backend.scrapeworker.scrape_worker import ScrapeWorker

app = typer.Typer()


async def start_worker_async():
    await init_db()
    worker_id = uuid4()
    while True:
        acquired = await SiteScrapeTask.get_motor_collection().find_one_and_update(
            {"status": "QUEUED"},
            {
                "$set": {
                    "start_time": datetime.now(),
                    "worker_id": worker_id,
                    "status": "IN_PROGRESS",
                }
            },
            sort=[("queued_time", pymongo.ASCENDING)],
            return_document=ReturnDocument.AFTER,
        )
        if acquired:
            scrape_task = SiteScrapeTask.parse_obj(acquired)
            site = await Site.get(scrape_task.site_id)
            if not site:
                raise Exception("Site not found")

            typer.secho(f"Acquired Task {scrape_task.id}", fg=typer.colors.BLUE)
            worker = ScrapeWorker(scrape_task, site)
            try:
                await worker.run_scrape()
                typer.secho(f"Finished Task {scrape_task.id}", fg=typer.colors.BLUE)
                now = datetime.now()
                await site.update(Set({
                    Site.last_status: "FINISHED",
                    Site.last_run_time: now
                }))
                await scrape_task.update(
                    Set({
                        SiteScrapeTask.status: "FINISHED",
                        SiteScrapeTask.end_time: now,
                    }))
            except Exception as ex:
                now = datetime.now()
                typer.secho(f"Task Failed {scrape_task.id}", fg=typer.colors.RED)
                await site.update(Set({
                    Site.last_status: "FAILED",
                    Site.last_run_time: now,
                }))
                await scrape_task.update(
                    Set({
                        SiteScrapeTask.status: "FAILED",
                        SiteScrapeTask.end_time: now,
                    }))
                raise ex
        await asyncio.sleep(5)


@app.command()
def start_worker():
    typer.secho(f"Starting Scrape Worder", fg=typer.colors.GREEN)
    asyncio.run(start_worker_async())


if __name__ == "__main__":
    app()
