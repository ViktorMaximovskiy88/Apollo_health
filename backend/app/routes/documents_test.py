from datetime import datetime, timedelta, timezone
from random import random

import pytest
import pytest_asyncio
import aiofiles
from pydantic import HttpUrl
from beanie import Document, PydanticObjectId
from fastapi import UploadFile
import requests
import tempfile

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

def simple_manual_retrieved_document(
    site: Site, 
    scrape_task: SiteScrapeTask,
    checksum = "test",
    text_checksum = "test",
    content_type = None,
    file_extension = None,
    metadata = {},
    doc_type_confidence = None,
    therapy_tags = [],
    indication_tags = [],
    identified_dates = []

) -> RetrievedDocument:
    return RetrievedDocument(
        name="test",
        url="https://www.example.com",
        lang_code="en",
        document_type="Authorization Policy",
        checksum=checksum,
        text_checksum=text_checksum,
        site_id=site.id,
        scrape_task_id=scrape_task.id,
        content_type=content_type,
        file_extension=file_extension,
        metadata=metadata,
        doc_type_confidence=doc_type_confidence,
        therapy_tags=therapy_tags,
        indication_tags=indication_tags,
        identified_dates=identified_dates
    )

class TestGetDocuments:
    def simple_doc(
        self,
        site: Site,
        scrape_task: SiteScrapeTask,
        first_collected_date: datetime,
    ) -> RetrievedDocument:
        doc = RetrievedDocument(
            name="test",
            url="https://www.example.com/",
            checksum="test",
            text_checksum="test",
            site_id=site.id,
            scrape_task_id=scrape_task.id,
            first_collected_date=first_collected_date,
        )
        return doc

    async def populate_db(self):
        await init_db(mock=True)
        site = simple_site(collection_method=CollectionMethod.Automated)
        await site.save()

        scrapes: list[SiteScrapeTask] = []
        for i in range(2):
            scrape = simple_scrape(site)
            await scrape.save()
            scrapes.append(scrape)

        docs: list[RetrievedDocument] = []
        for i in range(3):
            first_collected_date = datetime.now(tz=timezone.utc) + timedelta(hours=i)
            doc = self.simple_doc(site, scrapes[i % 2], first_collected_date)
            await doc.save()
            docs.append(doc)

        return docs, scrapes, site

    @pytest.mark.asyncio
    async def test_get_one_document_by_scrape(self):
        [docs, scrapes, site] = await self.populate_db()

        scrapes[0].retrieved_document_ids = [docs[0].id]
        scrapes[1].retrieved_document_ids = [docs[1].id, docs[2].id]
        for scrape in scrapes:
            await scrape.save()

        first_ret_docs = await get_documents(scrape_task_id=scrapes[0].id)
        second_ret_docs = await get_documents(scrape_task_id=scrapes[1].id)
        assert len(first_ret_docs) == 1
        found_site = first_ret_docs[0]
        assert found_site.id == docs[0].id
        assert len(second_ret_docs) == 2

    @pytest.mark.asyncio
    async def test_get_two_documents_by_scrape(self):
        [docs, scrapes, site] = await self.populate_db()

        scrapes[0].retrieved_document_ids = [docs[0].id]
        scrapes[1].retrieved_document_ids = [docs[2].id, docs[1].id]
        for scrape in scrapes:
            await scrape.save()

        first_ret_docs = await get_documents(scrape_task_id=scrapes[0].id)
        second_ret_docs = await get_documents(scrape_task_id=scrapes[1].id)
        assert len(first_ret_docs) == 1
        assert len(second_ret_docs) == 2
        found_site_one = second_ret_docs[0]
        found_site_two = second_ret_docs[1]
        assert found_site_one.id == docs[2].id
        assert found_site_two.id == docs[1].id
        assert found_site_one.first_collected_date > found_site_two.first_collected_date

    @pytest.mark.asyncio
    async def test_get_no_documents_by_scrape(self):
        [docs, scrapes, site] = await self.populate_db()

        scrapes[1].retrieved_document_ids = [docs[2].id, docs[1].id]
        for scrape in scrapes:
            await scrape.save()

        first_ret_docs = await get_documents(scrape_task_id=scrapes[0].id)
        second_ret_docs = await get_documents(scrape_task_id=scrapes[1].id)
        assert len(first_ret_docs) == 0
        assert len(second_ret_docs) == 2
        found_site_one = second_ret_docs[0]
        found_site_two = second_ret_docs[1]
        assert found_site_one.id == docs[2].id
        assert found_site_two.id == docs[1].id

    @pytest.mark.asyncio
    async def test_get_documents_by_content_extraction(self):
        [docs, scrapes, site] = await self.populate_db()

        scrapes[0].retrieved_document_ids = [docs[0].id]
        scrapes[1].retrieved_document_ids = [docs[2].id, docs[1].id]
        for scrape in scrapes:
            await scrape.save()

        ret_docs = await get_documents(automated_content_extraction=True)
        assert len(ret_docs) == 0

        second_ret_docs = await get_documents(
            scrape_task_id=scrapes[1].id, automated_content_extraction=False
        )
        assert len(second_ret_docs) == 2

    @pytest.mark.asyncio
    async def test_get_documents_by_site(self):
        [docs, scrapes, site] = await self.populate_db()

        scrapes[0].retrieved_document_ids = [docs[0].id]
        scrapes[1].retrieved_document_ids = [docs[2].id, docs[1].id]
        for scrape in scrapes:
            await scrape.save()

        docs[1].site_id = None
        await docs[1].save()

        ret_docs = await get_documents(site_id=site.id)
        assert len(ret_docs) == 2
        assert ret_docs[0].id == docs[2].id

        second_ret_docs = await get_documents(scrape_task_id=scrapes[1].id, site_id=site.id)
        assert len(second_ret_docs) == 1
        assert second_ret_docs[0].id == docs[2].id


class TestUploadFile:
    @pytest.mark.asyncio
    async def test_upload_file(self):
        URL = "https://parprdusemmitst01.blob.core.windows.net/autohunteddocs/7c8418d4-054b-4fa4-9b97-d3f75c353dd1/7c8418d4-054b-4fa4-9b97-d3f75c353dd1.pdf"  # noqa
        response = requests.get(URL)
        with tempfile.NamedTemporaryFile() as temp:
            async with aiofiles.open(temp.name, "wb") as fd:
                await fd.write(response.content)
                
                upload_file = UploadFile(filename="test.pdf", file=temp, content_type="application/pdf")
                uploaded_document = await upload_document(upload_file, User, MockLogger)

                assert uploaded_document['success'] == True
                assert uploaded_document['data']['checksum'] != None
                assert uploaded_document['data']['text_checksum'] != None
                assert uploaded_document['data']['metadata'] != None
                assert uploaded_document['data']['doc_type_confidence'] != None
    

    @pytest.mark.asyncio
    async def test_upload_create_document(self):
        URL = "https://parprdusemmitst01.blob.core.windows.net/autohunteddocs/7c8418d4-054b-4fa4-9b97-d3f75c353dd1/7c8418d4-054b-4fa4-9b97-d3f75c353dd1.pdf"  # noqa
        response = requests.get(URL)
        with tempfile.NamedTemporaryFile() as temp:
            async with aiofiles.open(temp.name, "wb") as fd:
                await fd.write(response.content)

                upload_file = UploadFile(filename="test.pdf", file=temp, content_type="application/pdf")
                uploaded_document = await upload_document(upload_file, User, MockLogger)
                
                assert uploaded_document['success'] == True
                site_one = await simple_site(collection_method=CollectionMethod.Manual).save()
                scrape_one = await simple_scrape(site_one, status=TaskStatus.IN_PROGRESS).save()
                doc = simple_manual_retrieved_document(
                    site_one, 
                    scrape_one,
                    checksum=uploaded_document['data']['checksum'],
                    text_checksum=uploaded_document['data']['text_checksum'],
                    content_type=uploaded_document['data']['content_type'],
                    file_extension=uploaded_document['data']['file_extension'],
                    metadata=uploaded_document['data']['metadata'],
                    doc_type_confidence=uploaded_document['data']['doc_type_confidence'],
                    therapy_tags=uploaded_document['data']['therapy_tags'],
                    indication_tags=uploaded_document['data']['indication_tags'],
                    identified_dates=uploaded_document['data']['identified_dates'],
                )
                user = User(
                    email="example@me.com",
                    full_name="John Doe",
                    hashed_password="example"
                )
                await user.save()
                
                doc_data = await add_document(doc, user, MockLogger)
                assert doc_data['success'] == True
                uploaded_document_2 = await upload_document(upload_file, User, MockLogger)

                assert uploaded_document_2['error'] == "The document already exists!"



class TestCreateDocuments:
    @pytest.mark.asyncio
    async def test_create_document(self):
        site_one = await simple_site(collection_method=CollectionMethod.Manual).save()
        scrape_one = await simple_scrape(site_one, status=TaskStatus.IN_PROGRESS).save()
        doc = simple_manual_retrieved_document(site_one, scrape_one)
        
        user = User(
            email="example@me.com",
            full_name="John Doe",
            hashed_password="example"
        )
        await user.save()

        doc_data = await add_document(doc, user, MockLogger)
        assert doc_data == {"success": True}

        first_ret_docs = await get_documents(scrape_task_id=scrape_one.id)
        assert len(first_ret_docs) == 1








