from functools import cache

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from backend.common.db.settings import settings
from backend.common.models.app_config import AppConfig
from backend.common.models.change_log import ChangeLog
from backend.common.models.comment import Comment
from backend.common.models.content_extraction_task import (
    ContentExtractionResult,
    ContentExtractionTask,
)
from backend.common.models.doc_document import DocDocument
from backend.common.models.document import RetrievedDocument
from backend.common.models.document_family import DocumentFamily
from backend.common.models.indication import Indication
from backend.common.models.lineage import DocumentAnalysis
from backend.common.models.link_task_log import LinkBaseTask, LinkRetrievedTask, LinkTaskLog
from backend.common.models.payer_backbone import (
    MCO,
    UMP,
    BenefitManager,
    Formulary,
    PayerBackboneUnionDoc,
    PayerParent,
    Plan,
    PlanBenefit,
)
from backend.common.models.payer_family import PayerFamily
from backend.common.models.proxy import Proxy
from backend.common.models.search_codes import SearchCodeSet
from backend.common.models.site import Site
from backend.common.models.site_scrape_task import SiteScrapeTask
from backend.common.models.tasks import TaskLog
from backend.common.models.translation_config import TranslationConfig
from backend.common.models.user import User
from backend.common.models.work_queue import WorkQueue


@cache
def get_motor_client(mock=False) -> AsyncIOMotorClient:
    if mock:
        from mongomock_motor import AsyncMongoMockClient

        client = AsyncMongoMockClient()
    else:
        client = AsyncIOMotorClient(
            settings.mongo_url,
            username=settings.mongo_user,
            password=settings.mongo_password,
        )
    return client


def get_motor_db(mock=False, database_name=None) -> AsyncIOMotorDatabase:
    if not database_name:
        database_name = settings.mongo_db
    return get_motor_client(mock)[database_name]


async def init_db(mock=False, database_name=None):
    await init_beanie(
        database=get_motor_db(mock, database_name),
        document_models=[
            User,
            Site,
            AppConfig,
            Proxy,
            Comment,
            WorkQueue,
            ChangeLog,
            Indication,
            DocDocument,
            SiteScrapeTask,
            TranslationConfig,
            RetrievedDocument,
            ContentExtractionTask,
            ContentExtractionResult,
            LinkTaskLog,
            LinkBaseTask,
            LinkRetrievedTask,
            DocumentFamily,
            DocumentAnalysis,
            PayerBackboneUnionDoc,
            PayerFamily,
            PlanBenefit,
            Plan,
            PayerParent,
            BenefitManager,
            UMP,
            MCO,
            Formulary,
            SearchCodeSet,
            TaskLog,
        ],  # type: ignore
    )
