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
from backend.common.models.content_extraction_task import ContentExtractionTask
from backend.common.models.document import RetrievedDocument
from backend.parseworker.extract_worker import ExtractWorker

from backend.common.db.init import init_db
from backend.common.models.site import Site
from backend.common.core.enums import TaskStatus

app = typer.Typer()


async def start_worker_async():
    await init_db()
    worker_id = uuid4()
    while True:
        acquired = (
            await ContentExtractionTask.get_motor_collection().find_one_and_update(
                {"status": TaskStatus.QUEUED},
                {
                    "$set": {
                        "start_time": datetime.now(),
                        "worker_id": worker_id,
                        "status": TaskStatus.IN_PROGRESS,
                    }
                },
                sort=[("queued_time", pymongo.ASCENDING)],
                return_document=ReturnDocument.AFTER,
            )
        )
        if acquired:
            extract_task = ContentExtractionTask.parse_obj(acquired)
            site = await Site.find_one(Site.id == extract_task.site_id)
            doc = await RetrievedDocument.find_one(
                RetrievedDocument.id == extract_task.retrieved_document_id
            )
            if not site or not doc:
                raise Exception("Site not found")

            typer.secho(f"Acquired Task {extract_task.id}", fg=typer.colors.BLUE)
            worker = ExtractWorker(extract_task, doc, site)
            try:
                await worker.run_extraction()
                typer.secho(f"Finished Task {extract_task.id}", fg=typer.colors.BLUE)
                now = datetime.now()
                await extract_task.update(
                    Set(
                        {
                            ContentExtractionTask.status: TaskStatus.FINISHED,
                            ContentExtractionTask.end_time: now,
                        }
                    )
                )
            except Exception as ex:
                now = datetime.now()
                typer.secho(f"Task Failed {extract_task.id}", fg=typer.colors.RED)
                await extract_task.update(
                    Set(
                        {
                            ContentExtractionTask.status: TaskStatus.FAILED,
                            ContentExtractionTask.end_time: now,
                        }
                    )
                )
                raise ex
        await asyncio.sleep(5)


@app.command()
def start_worker():
    typer.secho(f"Starting Parse Worker", fg=typer.colors.GREEN)
    asyncio.run(start_worker_async())


if __name__ == "__main__":
    app()
