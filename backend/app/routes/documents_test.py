from datetime import datetime, timedelta, timezone
from random import random

import pytest
import pytest_asyncio
import aiofiles
import os
from pydantic import HttpUrl
from fastapi import UploadFile
from beanie import Document

from backend.common.core.enums import CollectionMethod, SiteStatus, TaskStatus
from backend.common.db.init import init_db
from backend.common.models.document import RetrievedDocument, RetrievedDocumentLimitTags
from backend.common.models.site import BaseUrl, ScrapeMethodConfiguration, Site
from backend.common.models.site_scrape_task import SiteScrapeTask
from backend.common.models.user import User
from backend.app.routes.documents import (
    get_documents,
    add_document,
    upload_document
)

RetrievedDocumentLimitTags.Settings.projection = None  # type: ignore

@pytest_asyncio.fixture(autouse=True)
async def before_each_test():
    random_name = str(random())
    await init_db(mock=True, database_name=random_name)

class MockLogger:
    async def background_log_change(current_user: User, site_scrape_task: Document, action: str):
        assert type(current_user) == type(User)
        assert type(action) == str
        return None

def simple_scrape(site: Site, status=TaskStatus.QUEUED) -> SiteScrapeTask:
    return SiteScrapeTask(
        site_id=site.id,
        status=status,
        queued_time=datetime.now(tz=timezone.utc),
    )

def simple_site(
    disabled=False,
    base_urls=[BaseUrl(url=HttpUrl("https://www.example.com/", scheme="https"), status="ACTIVE")],
    collection_method=CollectionMethod.Automated,
    status=SiteStatus.ONLINE,
    last_run_status=None,
) -> Site:
    return Site(
        name="Test",
        collection_method=collection_method,
        scrape_method="",
        scrape_method_configuration=ScrapeMethodConfiguration(
            document_extensions=[],
            url_keywords=[],
            proxy_exclusions=[],
            follow_links=False,
            follow_link_keywords=[],
            follow_link_url_keywords=[],
        ),
        disabled=disabled,
        last_run_status=last_run_status,
        status=status,
        cron="0 * * * *",
        base_urls=base_urls,
    )

def simple_manual_retrieved_document(site: Site, scrape_task: SiteScrapeTask) -> RetrievedDocument:
    return RetrievedDocument(
            name="test",
            url="https://www.example.com",
            lang_code="en",
            document_type="Authorization Policy",
            checksum="test",
            text_checksum="test",
            site_id=site.id,
            scrape_task_id=scrape_task.id
        )

# class TestGetDocuments:
#     def simple_site(self):
#         site = Site(
#             name="Test",
#             scrape_method="",
#             scrape_method_configuration=ScrapeMethodConfiguration(
#                 document_extensions=[],
#                 url_keywords=[],
#                 proxy_exclusions=[],
#                 follow_links=False,
#                 follow_link_keywords=[],
#                 follow_link_url_keywords=[],
#             ),
#             disabled=False,
#             cron="5 * * * *",
#             base_urls=[
#                 BaseUrl(
#                     url=HttpUrl("https://www.example.com/", scheme="https"),
#                     status="ACTIVE",
#                 )
#             ],
#         )
#         return site

#     def simple_doc(
#         self,
#         site: Site,
#         scrape_task: SiteScrapeTask,
#         first_collected_date: datetime,
#     ) -> RetrievedDocument:
#         doc = RetrievedDocument(
#             name="test",
#             checksum="test",
#             text_checksum="test",
#             site_id=site.id,
#             scrape_task_id=scrape_task.id,
#             first_collected_date=first_collected_date,
#         )
#         return doc

#     def simple_scrape(
#         self,
#         site: Site,
#     ) -> SiteScrapeTask:
#         scrape = SiteScrapeTask(
#             site_id=site.id,
#             queued_time=datetime.now(tz=timezone.utc),
#         )
#         return scrape

#     async def populate_db(self):
#         await init_db(mock=True)
#         site = self.simple_site()
#         await site.save()

#         scrapes: list[SiteScrapeTask] = []
#         for i in range(2):
#             scrape = self.simple_scrape(site)
#             await scrape.save()
#             scrapes.append(scrape)

#         docs: list[RetrievedDocument] = []
#         for i in range(3):
#             first_collected_date = datetime.now(tz=timezone.utc) + timedelta(hours=i)
#             doc = self.simple_doc(site, scrapes[i % 2], first_collected_date)
#             await doc.save()
#             docs.append(doc)

#         return docs, scrapes, site

#     @pytest.mark.asyncio
#     async def test_get_one_document_by_scrape(self):
#         [docs, scrapes, site] = await self.populate_db()

#         scrapes[0].retrieved_document_ids = [docs[0].id]
#         scrapes[1].retrieved_document_ids = [docs[1].id, docs[2].id]
#         for scrape in scrapes:
#             await scrape.save()

#         first_ret_docs = await get_documents(scrape_task_id=scrapes[0].id)
#         second_ret_docs = await get_documents(scrape_task_id=scrapes[1].id)
#         assert len(first_ret_docs) == 1
#         found_site = first_ret_docs[0]
#         assert found_site.id == docs[0].id
#         assert len(second_ret_docs) == 2

#     @pytest.mark.asyncio
#     async def test_get_two_documents_by_scrape(self):
#         [docs, scrapes, site] = await self.populate_db()

#         scrapes[0].retrieved_document_ids = [docs[0].id]
#         scrapes[1].retrieved_document_ids = [docs[2].id, docs[1].id]
#         for scrape in scrapes:
#             await scrape.save()

#         first_ret_docs = await get_documents(scrape_task_id=scrapes[0].id)
#         second_ret_docs = await get_documents(scrape_task_id=scrapes[1].id)
#         assert len(first_ret_docs) == 1
#         assert len(second_ret_docs) == 2
#         found_site_one = second_ret_docs[0]
#         found_site_two = second_ret_docs[1]
#         assert found_site_one.id == docs[2].id
#         assert found_site_two.id == docs[1].id
#         assert found_site_one.first_collected_date > found_site_two.first_collected_date

#     @pytest.mark.asyncio
#     async def test_get_no_documents_by_scrape(self):
#         [docs, scrapes, site] = await self.populate_db()

#         scrapes[1].retrieved_document_ids = [docs[2].id, docs[1].id]
#         for scrape in scrapes:
#             await scrape.save()

#         first_ret_docs = await get_documents(scrape_task_id=scrapes[0].id)
#         second_ret_docs = await get_documents(scrape_task_id=scrapes[1].id)
#         assert len(first_ret_docs) == 0
#         assert len(second_ret_docs) == 2
#         found_site_one = second_ret_docs[0]
#         found_site_two = second_ret_docs[1]
#         assert found_site_one.id == docs[2].id
#         assert found_site_two.id == docs[1].id

#     @pytest.mark.asyncio
#     async def test_get_documents_by_content_extraction(self):
#         [docs, scrapes, site] = await self.populate_db()

#         scrapes[0].retrieved_document_ids = [docs[0].id]
#         scrapes[1].retrieved_document_ids = [docs[2].id, docs[1].id]
#         for scrape in scrapes:
#             await scrape.save()

#         ret_docs = await get_documents(automated_content_extraction=True)
#         assert len(ret_docs) == 0

#         second_ret_docs = await get_documents(
#             scrape_task_id=scrapes[1].id, automated_content_extraction=False
#         )
#         assert len(second_ret_docs) == 2

#     @pytest.mark.asyncio
#     async def test_get_documents_by_site(self):
#         [docs, scrapes, site] = await self.populate_db()

#         scrapes[0].retrieved_document_ids = [docs[0].id]
#         scrapes[1].retrieved_document_ids = [docs[2].id, docs[1].id]
#         for scrape in scrapes:
#             await scrape.save()

#         docs[1].site_id = None
#         await docs[1].save()

#         ret_docs = await get_documents(site_id=site.id)
#         assert len(ret_docs) == 2
#         assert ret_docs[0].id == docs[2].id

#         second_ret_docs = await get_documents(scrape_task_id=scrapes[1].id, site_id=site.id)
#         assert len(second_ret_docs) == 1
#         assert second_ret_docs[0].id == docs[2].id



class TestUploadFile:
    @pytest.mark.asyncio
    async def test_upload_file(self):
        current_path = os.path.dirname(os.path.abspath('__file__'))
        file_path = os.path.join(current_path,'backend', 'common', 'storage','__fixtures__', 'example-desktop-word.docx')

        async with aiofiles.open(file_path, mode="wb+") as f:
            # upload = await upload_document(f, User, MockLogger)
            print(f)




# class TestCreateDocuments:
#     @pytest.mark.asyncio
#     async def test_create_document(self):
#         site_one = await simple_site(collection_method=CollectionMethod.Manual).save()
#         scrape_one = await simple_scrape(site_one, status=TaskStatus.IN_PROGRESS).save()
#         doc = simple_manual_retrieved_document(site_one, scrape_one)
#         doc_data = await add_document(doc, User, MockLogger)

#         assert doc_data == {"success": True}

#         first_ret_docs = await get_documents(scrape_task_id=scrape_one.id)
#         assert len(first_ret_docs) == 1































