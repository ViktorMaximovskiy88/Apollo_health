from datetime import datetime
from random import random

import pytest_asyncio
from beanie import PydanticObjectId

from backend.common.core.enums import ApprovalStatus, ScrapeMethod
from backend.common.db.init import init_db
from backend.common.models import User
from backend.common.models.doc_document import DocDocument, DocDocumentLocation, UpdateDocDocument
from backend.common.models.document import RetrievedDocument, RetrievedDocumentLocation
from backend.common.models.site import ScrapeMethodConfiguration, Site
from backend.common.repositories.doc_document_repository import DocDocumentRepository
from backend.common.services.doc_lifecycle.hooks import ChangeInfo


@pytest_asyncio.fixture(autouse=True)
async def before_each_test():
    random_name = str(random())
    await init_db(mock=True, database_name=random_name)


@pytest_asyncio.fixture(autouse=True)
async def site():
    site = await Site(
        name="Test",
        scrape_method=ScrapeMethod.Simple,
        scrape_method_configuration=ScrapeMethodConfiguration(
            document_extensions=[],
            url_keywords=[],
            proxy_exclusions=[],
            follow_links=False,
            follow_link_keywords=[],
            follow_link_url_keywords=[],
        ),
        disabled=False,
        cron="0 * * * *",
    ).save()
    return site


@pytest_asyncio.fixture(autouse=True)
async def simple_ret_doc(site: Site) -> RetrievedDocument:
    doc = await RetrievedDocument(
        name="test",
        checksum="test",
        text_checksum="test",
        first_collected_date=datetime.now(),
        last_collected_date=datetime.now(),
        locations=[
            RetrievedDocumentLocation(
                site_id=site.id,
                first_collected_date=datetime.now(),
                last_collected_date=datetime.now(),
                url="https://www.example.com/doc",
                base_url="https://www.example.com/",
                link_text="",
                closest_heading="",
                siblings_text=None,
            )
        ],
    ).save()
    return doc


@pytest_asyncio.fixture(autouse=True)
async def simple_doc_doc(site: Site, simple_ret_doc: RetrievedDocument):
    doc = await DocDocument(
        name="test",
        retrieved_document_id=simple_ret_doc.id,
        checksum="test",
        text_checksum="test",
        document_type="Treatment Request Form",
        first_collected_date=datetime.now(),
        family_status=ApprovalStatus.APPROVED,
        last_collected_date=datetime.now(),
        last_updated_date=datetime.now(),
        document_family_id=PydanticObjectId(),
        classification_status=ApprovalStatus.APPROVED,
        locations=[
            DocDocumentLocation(
                site_id=site.id,
                first_collected_date=datetime.now(),
                last_collected_date=datetime.now(),
                url="https://www.example.com/doc",
                base_url="https://www.example.com/",
                link_text="",
                closest_heading="",
                siblings_text=None,
            )
        ],
    ).save()
    return doc


@pytest_asyncio.fixture()
async def user():
    user = User(
        id=PydanticObjectId(),
        email="example@me.com",
        full_name="John Doe",
        hashed_password="example",
    )
    await user.save()

    return user


async def test_doc_document_pre_save(simple_doc_doc):
    updates = UpdateDocDocument(document_type="Authorization Policy")
    await DocDocumentRepository().pre_save(simple_doc_doc, updates)
    assert updates.document_family_id is None


async def test_doc_document_save(simple_doc_doc, user):
    updates = UpdateDocDocument(document_type="Authorization Policy")
    await DocDocumentRepository().save(simple_doc_doc, updates, user)
    doc = await DocDocument.find({"_id": simple_doc_doc.id}).to_list()
    assert doc[0].document_type == "Authorization Policy"


async def test_doc_document_post_save(simple_doc_doc, user):
    await simple_doc_doc.update({"$set": {"document_family_id": None}})
    doc_doc_repo = DocDocumentRepository()
    doc_doc_repo.change_info = ChangeInfo()
    await doc_doc_repo.post_save(simple_doc_doc, user)
    doc = await DocDocument.find({"_id": simple_doc_doc.id}).to_list()
    assert doc[0].status == ApprovalStatus.PENDING
