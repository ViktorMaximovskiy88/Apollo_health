from functools import cache
from beanie import init_beanie
from backend.common.db.settings import settings
from backend.common.models.change_log import ChangeLog
from backend.common.models.content_extraction_task import (
    ContentExtractionResult,
    ContentExtractionTask,
)

from backend.common.models.site import Site
from backend.common.models.site_scrape_task import SiteScrapeTask
from backend.common.models.user import User
from backend.common.models.document import RetrievedDocument

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase


@cache
def get_motor_client() -> AsyncIOMotorClient:
    client = AsyncIOMotorClient(
        settings.mongo_url,
        username=settings.mongo_user,
        password=settings.mongo_password,
    )
    return client


def get_motor_db() -> AsyncIOMotorDatabase:
    return get_motor_client()[settings.mongo_db]


async def init_db():
    await init_beanie(
        database=get_motor_db(),
        document_models=[
            User,
            ChangeLog,
            Site,
            SiteScrapeTask,
            RetrievedDocument,
            ContentExtractionTask,
            ContentExtractionResult,
        ],
    )
