import tempfile
from datetime import datetime, timedelta, timezone
from random import random

import aiofiles
import pytest
import pytest_asyncio
import requests
from beanie import Document, PydanticObjectId
from fastapi import UploadFile
from pydantic import HttpUrl

from backend.app.routes.documents import add_document, get_documents, upload_document
from backend.common.core.enums import CollectionMethod, LangCode, SiteStatus, TaskStatus
from backend.common.db.init import init_db
from backend.common.models.document import RetrievedDocument, RetrievedDocumentLimitTags
from backend.common.models.site import BaseUrl, ScrapeMethodConfiguration, Site
from backend.common.models.site_scrape_task import SiteScrapeTask
from backend.common.models.user import User

RetrievedDocumentLimitTags.Settings.projection = None  # type: ignore


@pytest_asyncio.fixture(autouse=True)
async def before_each_test():
    random_name = str(random())
    await init_db(mock=True, database_name=random_name)


@pytest_asyncio.fixture()
@pytest.mark.asyncio()
async def user():
    user = User(
        id=PydanticObjectId("62e7c6647e2a94f469d57f34"),
        email="example@me.com",
        full_name="John Doe",
        hashed_password="example",
    )
    await user.save()
    return user


class MockLogger:
    async def background_log_change(
        self, current_user: User, site_scrape_task: Document, action: str
    ):
        assert current_user.id is not None
        assert type(action) == str
        return None


@pytest_asyncio.fixture()
async def logger():
    return MockLogger()


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
    checksum="test",
    text_checksum="test",
    content_type=None,
    file_extension=None,
    metadata={},
    doc_type_confidence=None,
    therapy_tags=[],
    indication_tags=[],
    identified_dates=[],
) -> RetrievedDocument:
    return RetrievedDocument(
        name="test",
        url="https://www.example.com",
        lang_code=LangCode.English,
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
        identified_dates=identified_dates,
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

        scrapes[0].retrieved_document_ids = [docs[0].id]  # type: ignore
        scrapes[1].retrieved_document_ids = [docs[1].id, docs[2].id]  # type: ignore
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

        scrapes[0].retrieved_document_ids = [docs[0].id]  # type: ignore
        scrapes[1].retrieved_document_ids = [docs[2].id, docs[1].id]  # type: ignore
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
        assert found_site_one.first_collected_date > found_site_two.first_collected_date  # type: ignore # noqa: E501

    @pytest.mark.asyncio
    async def test_get_no_documents_by_scrape(self):
        [docs, scrapes, site] = await self.populate_db()

        scrapes[1].retrieved_document_ids = [docs[2].id, docs[1].id]  # type: ignore
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

        scrapes[0].retrieved_document_ids = [docs[0].id]  # type: ignore
        scrapes[1].retrieved_document_ids = [docs[2].id, docs[1].id]  # type: ignore
        for scrape in scrapes:
            await scrape.save()

        second_ret_docs = await get_documents(scrape_task_id=scrapes[1].id)
        assert len(second_ret_docs) == 2

    @pytest.mark.asyncio
    async def test_get_documents_by_site(self):
        [docs, scrapes, site] = await self.populate_db()

        scrapes[0].retrieved_document_ids = [docs[0].id]  # type: ignore
        scrapes[1].retrieved_document_ids = [docs[2].id, docs[1].id]  # type: ignore
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
    async def test_upload_file(self, user, logger):
        URL = "https://parprdusemmitst01.blob.core.windows.net/autohunteddocs/7c8418d4-054b-4fa4-9b97-d3f75c353dd1/7c8418d4-054b-4fa4-9b97-d3f75c353dd1.pdf"  # noqa
        response = requests.get(URL)
        with tempfile.NamedTemporaryFile() as temp:
            async with aiofiles.open(temp.name, "wb") as fd:
                await fd.write(response.content)

                upload_file = UploadFile(
                    filename="test.pdf", file=temp, content_type="application/pdf"
                )
                uploaded_document = await upload_document(upload_file, user, logger)

                assert uploaded_document["success"] is True
                assert uploaded_document["data"]["checksum"] is not None  # type: ignore
                assert uploaded_document["data"]["text_checksum"] is not None  # type: ignore
                assert uploaded_document["data"]["metadata"] is not None  # type: ignore
                assert uploaded_document["data"]["doc_type_confidence"] is not None  # type: ignore

    @pytest.mark.asyncio
    async def test_upload_create_document(self, user, logger):
        URL = "https://parprdusemmitst01.blob.core.windows.net/autohunteddocs/7c8418d4-054b-4fa4-9b97-d3f75c353dd1/7c8418d4-054b-4fa4-9b97-d3f75c353dd1.pdf"  # noqa
        response = requests.get(URL)
        with tempfile.NamedTemporaryFile() as temp:
            async with aiofiles.open(temp.name, "wb") as fd:
                await fd.write(response.content)

                upload_file = UploadFile(
                    filename="test.pdf", file=temp, content_type="application/pdf"
                )
                uploaded_document = await upload_document(upload_file, user, logger)

                assert uploaded_document["success"] is True
                site_one = await simple_site(collection_method=CollectionMethod.Manual).save()
                scrape_one = await simple_scrape(site_one, status=TaskStatus.IN_PROGRESS).save()
                doc = simple_manual_retrieved_document(
                    site_one,
                    scrape_one,
                    checksum=uploaded_document["data"]["checksum"],  # type: ignore
                    text_checksum=uploaded_document["data"]["text_checksum"],  # type: ignore
                    content_type=uploaded_document["data"]["content_type"],  # type: ignore
                    file_extension=uploaded_document["data"]["file_extension"],  # type: ignore
                    metadata=uploaded_document["data"]["metadata"],  # type: ignore
                    doc_type_confidence=uploaded_document["data"]["doc_type_confidence"],  # type: ignore # noqa: E501
                    therapy_tags=uploaded_document["data"]["therapy_tags"],  # type: ignore
                    indication_tags=uploaded_document["data"]["indication_tags"],  # type: ignore
                    identified_dates=uploaded_document["data"]["identified_dates"],  # type: ignore
                )

                doc_data = await add_document(doc, user, logger)
                assert doc_data["success"] is True
                uploaded_document_2 = await upload_document(upload_file, user, logger)

                assert uploaded_document_2["error"] == "The document already exists!"


class TestCreateDocuments:
    @pytest.mark.asyncio
    async def test_create_document(self, user, logger):
        site_one = await simple_site(collection_method=CollectionMethod.Manual).save()
        scrape_one = await simple_scrape(site_one, status=TaskStatus.IN_PROGRESS).save()
        doc = simple_manual_retrieved_document(site_one, scrape_one)

        doc_data = await add_document(doc, user, logger)
        assert doc_data == {"success": True}

        first_ret_docs = await get_documents(scrape_task_id=scrape_one.id)
        assert len(first_ret_docs) == 1
