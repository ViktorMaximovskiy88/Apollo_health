import asyncio
import sys
from pathlib import Path

import typer

sys.path.append(str(Path(__file__).parent.joinpath("../../..").resolve()))

from backend.app.core.settings import settings
from backend.common.models.site import Site
from backend.common.models.tasks import SiteDocsPipelineTask
from backend.common.models.user import User
from backend.common.tasks.task_queue import TaskQueue
from backend.parseworker.scripts.build_rxnorm_linker import main as build_rxnorm_linker
from backend.parseworker.scripts.set_tagging_model_version import (
    execute as set_tagging_model_version,
)
from backend.parseworker.scripts.upload_tagging_models import main as upload_tagging_models

task_queue = TaskQueue(
    queue_url=settings.task_worker_queue_url,
)


async def enqueue_site_docs_task():
    user = await User.get_api_user()
    async for site in Site.find():
        task_payload = SiteDocsPipelineTask(site_id=site.id, reprocess=False)
        await task_queue.enqueue(task_payload, user.id)


async def async_main(output_folder):
    build_rxnorm_linker(output_folder)
    upload_tagging_models(output_folder)
    await set_tagging_model_version(output_folder)
    print("enqueuing site doc tasks")
    await enqueue_site_docs_task()


def main(
    output_folder: Path = typer.Argument(None),
):
    asyncio.run(async_main(output_folder=output_folder))


if __name__ == "__main__":
    typer.run(main)
