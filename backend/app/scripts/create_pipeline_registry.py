import asyncio
import logging
from datetime import datetime, timezone

from backend.common.db.init import init_db
from backend.common.models.pipeline import PipelineRegistry, PipelineRegistryStage
from backend.common.models.user import User


async def get_user() -> User:
    user = await User.by_email("admin@mmitnetwork.com")
    if not user:
        raise Exception("Admin user not found")
    return user


async def create_pipeline_registry():
    exists = await PipelineRegistry.fetch()
    if not exists:
        now = datetime.now(tz=timezone.utc)
        user = await get_user()
        stage = PipelineRegistryStage(version=1, version_at=now, version_by=user.id)
        pending = PipelineRegistry(
            content=stage, date=stage, doc_type=stage, tag=stage, lineage=stage
        )
        result = await pending.save()
        logging.info(f"created pipeline registry with _id={result.id}")
    else:
        logging.info(f"existing pipeline registry with _id={exists.id}")


async def execute():
    await init_db()
    await create_pipeline_registry()


if __name__ == "__main__":
    asyncio.run(execute())
