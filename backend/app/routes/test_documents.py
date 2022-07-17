from datetime import datetime, timedelta

from pydantic import HttpUrl
import pytest

from backend.common.models.site import ScrapeMethodConfiguration
from backend.common.models.document import RetrievedDocument, RetrievedDocumentLimitTags
from backend.common.models.site_scrape_task import SiteScrapeTask
from backend.common.models.site import BaseUrl, ScrapeMethodConfiguration, Site
from backend.app.routes.documents import get_documents
from backend.common.db.init import init_db

RetrievedDocumentLimitTags.Settings.projection = None  # type: ignore

class TestGetDocuments:
    def simple_site(self):
        site = Site(
            name="Test",
            scrape_method="",
            scrape_method_configuration=ScrapeMethodConfiguration(
                document_extensions=[],
                url_keywords=[],
                proxy_exclusions=[],
                follow_links=False,
                follow_link_keywords=[],
                follow_link_url_keywords=[],
        ),
            disabled=False,
            cron="5 * * * *",
            base_urls=[
                BaseUrl(
                    url=HttpUrl("https://www.example.com/", scheme="https"),
                    status="ACTIVE",
                )
            ],
        )
        return site

    def simple_doc(
        self,
        site: Site,
        scrape_task: SiteScrapeTask,
        first_collected_date: datetime,
    ) -> RetrievedDocument:
        doc = RetrievedDocument(
            name='test',
            checksum='test',
            site_id=site.id,
            scrape_task_id=scrape_task.id,
            first_collected_date=first_collected_date,
        )
        return doc

    def simple_scrape(
        self,
        site: Site,
    ) -> SiteScrapeTask:
        scrape = SiteScrapeTask(
            site_id=site.id,
            queued_time=datetime.now(),
        )
        return scrape

    async def populate_db(self):
        await init_db(mock=True)
        site = self.simple_site()
        await site.save()

        scrapes: list[SiteScrapeTask] = []
        for i in range(2):
            scrape = self.simple_scrape(site)
            await scrape.save()
            scrapes.append(scrape)

        docs: list[RetrievedDocument] = []
        for i in range(3):
            first_collected_date = datetime.now() + timedelta(hours=i)
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

        second_ret_docs = await get_documents(
            scrape_task_id=scrapes[1].id, site_id=site.id
        )
        assert len(second_ret_docs) == 1
        assert second_ret_docs[0].id == docs[2].id
