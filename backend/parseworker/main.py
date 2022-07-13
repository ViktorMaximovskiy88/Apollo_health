import asyncio
import importlib
from pathlib import Path
import sys
import traceback
from uuid import uuid4
import typer

from datetime import datetime
import pymongo
from pymongo import ReturnDocument
from beanie.odm.operators.update.general import Set


sys.path.append(str(Path(__file__).parent.joinpath("../..").resolve()))
from backend.app.utils.logger import Logger, update_and_log_diff
from backend.common.models.doc_document import DocDocument, UpdateDocDocument
from backend.common.models.user import User
from backend.common.models.content_extraction_task import ContentExtractionTask
from backend.common.models.document import RetrievedDocument
from backend.parseworker.rxnorm_entity_linker_model import RxNormEntityLinkerModel

from backend.common.db.init import init_db
from backend.common.models.site import Site
from backend.common.core.enums import TaskStatus

app = typer.Typer()


async def start_worker_async():
    await init_db()
    worker_id = uuid4()
    rxnorm_model = RxNormEntityLinkerModel()
    extractor_classes = importlib.import_module("backend.parseworker.extractors")
    user = await User.by_email("admin@mmitnetwork.com")
    logger = Logger()
    if not user:
        raise Exception("No admin user found")

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
            doc_document = await DocDocument.find_one(
                DocDocument.retrieved_document_id == doc.id
            )
            if not doc_document:
                raise Exception("DocDocument not found")

            typer.secho(f"Acquired Task {extract_task.id}", fg=typer.colors.BLUE)

            extraction_class = (
                doc.automated_content_extraction_class or "BasicTableExtraction"
            )
            ExtractWorker = getattr(extractor_classes, extraction_class)

            worker = ExtractWorker(extract_task, doc, site, rxnorm_model)
            try:
                await worker.run_extraction()
                typer.secho(f"Finished Task {extract_task.id}", fg=typer.colors.BLUE)
                now = datetime.now()
                update = UpdateDocDocument(content_extraction_task_id=extract_task.id)
                await update_and_log_diff(logger, user, doc_document, update)
                await extract_task.update(
                    Set(
                        {
                            ContentExtractionTask.status: TaskStatus.FINISHED,
                            ContentExtractionTask.end_time: now,
                        }
                    )
                )
            except Exception as ex:
                message = traceback.format_exc()
                traceback.print_exc()
                now = datetime.now()
                typer.secho(f"Task Failed {extract_task.id}", fg=typer.colors.RED)
                await extract_task.update(
                    Set(
                        {
                            ContentExtractionTask.status: TaskStatus.FAILED,
                            ContentExtractionTask.end_time: now,
                            ContentExtractionTask.error_message: message,
                        }
                    )
                )
        await asyncio.sleep(5)


@app.command()
def start_worker():
    typer.secho(f"Starting Parse Worker", fg=typer.colors.GREEN)
    asyncio.run(start_worker_async())


if __name__ == "__main__":
    app()
