import asyncio
import os
import sys
from pathlib import Path

import typer

from backend.common.storage.client import ModelStorageClient

sys.path.append(str(Path(__file__).parent.joinpath("../../..").resolve()))
from backend.common.core.utils import now
from backend.common.db.init import init_db
from backend.common.models.app_config import AppConfig
from backend.common.models.pipeline import PipelineRegistry, PipelineRegistryStage
from backend.common.models.user import User


async def execute(version):

    await init_db()

    # Refuse to update model version if associated files don't exist
    client = ModelStorageClient()
    if not client.object_exists(f"{version}/rxnorm/rxnorm.jsonl"):
        raise Exception(f"Model {version} rxnorm does not exist in {os.getenv('ENV_TYPE')} env!")
    if not client.object_exists(f"{version}/rxnorm-span/meta.json"):
        raise Exception(
            f"Model {version} rxnorm-span does not exist in {os.getenv('ENV_TYPE')} env!"
        )
    if not client.object_exists(f"{version}/indication/meta.json"):
        raise Exception(
            f"Model {version} rxnorm-span does not exist in {os.getenv('ENV_TYPE')} env!"
        )

    data = {
        "indication": version,
        "rxnorm-span": version,
        "rxnorm": version,
    }

    app_config = AppConfig(key="model_versions", data=data)
    await AppConfig.find({"key": "model_versions"}).upsert(
        {"$set": {"data": data}}, on_insert=app_config
    )

    stage_versions = await PipelineRegistry.fetch()
    user = await User.get_api_user()
    stage_versions.tag = PipelineRegistryStage(
        version=str(version),
        version_at=now(),
        version_by=user.id,
    )
    await stage_versions.save()


if __name__ == "__main__":

    def main(version: str = typer.Argument(None)):
        asyncio.run(execute(version))

    typer.run(main)
