from pathlib import Path

import newrelic.agent

from backend.common.services.doc_lifecycle.hooks import doc_document_save_hook

newrelic.agent.initialize(Path(__file__).parent / "newrelic.ini")

import asyncio
import logging
import sys
import traceback
from datetime import datetime, timezone
from uuid import uuid4

import pymongo
import typer
from beanie.odm.operators.update.general import Set
from pymongo import ReturnDocument

sys.path.append(str(Path(__file__).parent.joinpath("../..").resolve()))
from backend.common.core.enums import TaskStatus
from backend.common.db.init import init_db
from backend.common.models.content_extraction_task import ContentExtractionTask
from backend.common.models.doc_document import DocDocument
from backend.common.models.translation_config import TranslationConfig
from backend.common.models.user import User
from backend.parseworker.extractor import TableContentExtractor

app = typer.Typer()


async def start_worker_async():
    await init_db()
    worker_id = uuid4()
    user = await User.by_email("admin@mmitnetwork.com")
    if not user:
        raise Exception("No admin user found")

    while True:
        acquired = await ContentExtractionTask.get_motor_collection().find_one_and_update(
            {"status": TaskStatus.QUEUED},
            {
                "$set": {
                    "start_time": datetime.now(tz=timezone.utc),
                    "worker_id": worker_id,
                    "status": TaskStatus.IN_PROGRESS,
                }
            },
            sort=[("queued_time", pymongo.ASCENDING)],
            return_document=ReturnDocument.AFTER,
        )
        if acquired:
            extract_task = ContentExtractionTask.parse_obj(acquired)
            doc_document = await DocDocument.find_one(
                DocDocument.id == extract_task.doc_document_id
            )
            if not doc_document:
                raise Exception("DocDocument not found")
            if not doc_document.translation_id:
                raise Exception("DocDocument does not have translation_id")

            config = await TranslationConfig.get(doc_document.translation_id)
            if not config:
                raise Exception("TranslationConfig not found")

            typer.secho(f"Acquired Task {extract_task.id}", fg=typer.colors.BLUE)

            worker = TableContentExtractor(doc_document, config)
            try:
                await worker.run_extraction(extract_task)
                await worker.calculate_delta(extract_task)

                typer.secho(f"Finished Task {extract_task.id}", fg=typer.colors.BLUE)
                now = datetime.now(tz=timezone.utc)
                await asyncio.gather(
                    doc_document.update(Set({"content_extraction_task_id": extract_task.id})),
                    extract_task.update(
                        Set(
                            {
                                ContentExtractionTask.status: TaskStatus.FINISHED,
                                ContentExtractionTask.end_time: now,
                            }
                        )
                    ),
                )
            except Exception as ex:
                logging.error(ex)
                message = traceback.format_exc()
                traceback.print_exc()
                now = datetime.now(tz=timezone.utc)
                typer.secho(f"Task Failed {extract_task.id}", fg=typer.colors.RED)
                await asyncio.gather(
                    doc_document.update(Set({"content_extraction_task_id": extract_task.id})),
                    extract_task.update(
                        Set(
                            {
                                ContentExtractionTask.status: TaskStatus.FAILED,
                                ContentExtractionTask.end_time: now,
                                ContentExtractionTask.error_message: message,
                            }
                        )
                    ),
                )
            await doc_document_save_hook(doc_document)
        await asyncio.sleep(5)


@app.command()
def start_worker():
    typer.secho("Starting Parse Worker", fg=typer.colors.GREEN)
    asyncio.run(start_worker_async())


if __name__ == "__main__":
    app()
