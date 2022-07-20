from beanie import Document
from datetime import datetime
import pytest
import pytest_asyncio
from random import random

from backend.app.routes.site_scrape_tasks import runBulkByType
from backend.common.core.enums import SiteStatus, TaskStatus
from backend.common.core.enums import CollectionMethod
from backend.common.db.init import init_db
from backend.common.models.site import BaseUrl, HttpUrl, ScrapeMethodConfiguration, Site
from backend.common.models.site_scrape_task import SiteScrapeTask
from backend.common.models.user import User


@pytest_asyncio.fixture(autouse=True)
async def before_each_test():
    random_name = str(random())
    await init_db(mock=True, database_name=random_name)


class MockLogger:
    async def background_log_change(
        current_user: User, site_scrape_task: Document, action: str
    ):
        assert type(current_user) == type(User)
        assert type(action) == str
        return None


class TestRunBulk:
    def simple_site(
        self,
        disabled=False,
        base_urls=[
            BaseUrl(
                url=HttpUrl("https://www.example.com/", scheme="https"), status="ACTIVE"
            )
        ],
        collection_method=CollectionMethod.Automated,
        status=SiteStatus.ONLINE,
        last_run_status=None,
    ):
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

    def simple_scrape(
        self,
        site: Site,
    ) -> SiteScrapeTask:
        scrape = SiteScrapeTask(
            site_id=site.id,
            status=TaskStatus.QUEUED,
            queued_time=datetime.now(),
        )
        return scrape

    @pytest.mark.asyncio
    async def test_run_unrun(self):
        site_one = await self.simple_site().save()
        await self.simple_site(last_run_status=TaskStatus.FAILED).save()

        res = await runBulkByType("unrun", MockLogger, User)
        assert res == {"status": True, "scrapes_launched": 1}
        scrape = await SiteScrapeTask.find({"site_id": site_one.id}).to_list()
        assert len(scrape) == 1

    @pytest.mark.asyncio
    async def test_run_failed(self):
        site_one = await self.simple_site(last_run_status=TaskStatus.FAILED).save()
        site_two = await self.simple_site(last_run_status=TaskStatus.CANCELED).save()
        await self.simple_site().save()

        res = await runBulkByType("failed", MockLogger, User)
        assert res == {"status": True, "scrapes_launched": 2}
        scrapes = await SiteScrapeTask.find(
            {"site_id": {"$in": [site_one.id, site_two.id]}}
        ).to_list()
        assert len(scrapes) == 2

    @pytest.mark.asyncio
    async def test_run_canceled(self):
        site_one = await self.simple_site(last_run_status=TaskStatus.CANCELED).save()
        await self.simple_site().save()

        res = await runBulkByType("failed", MockLogger, User)
        assert res == {"status": True, "scrapes_launched": 1}
        scrapes = await SiteScrapeTask.find({"site_id": site_one.id}).to_list()
        assert len(scrapes) == 1

    @pytest.mark.asyncio
    async def test_run_all(self):
        site_one = await self.simple_site().save()
        await self.simple_site(last_run_status=TaskStatus.QUEUED).save()
        await self.simple_site(last_run_status=TaskStatus.IN_PROGRESS).save()

        res = await runBulkByType("all", MockLogger, User)
        assert res == {"status": True, "scrapes_launched": 1}
        scrapes = await SiteScrapeTask.find({"site_id": site_one.id}).to_list()
        assert len(scrapes) == 1

    @pytest.mark.asyncio
    async def test_run_no_scrapes(self):
        sites: list[Site] = []
        sites.append(self.simple_site(disabled=True))
        sites.append(self.simple_site(base_urls=[]))
        sites.append(self.simple_site(collection_method=CollectionMethod.Manual))
        sites.append(self.simple_site(status=SiteStatus.INACTIVE))
        await Site.insert_many(sites)

        bulk_types = ["unrun", "failed", "canceled", "all"]
        for bulk_type in bulk_types:
            res = await runBulkByType(bulk_type, MockLogger, User)
            assert res == {"status": True, "scrapes_launched": 0}

        scrapes = await SiteScrapeTask.find({}).to_list()
        assert len(scrapes) == 0

    @pytest.mark.asyncio
    async def test_cancel_active(self):
        site_one = await self.simple_site(
            status=SiteStatus.INACTIVE, last_run_status=TaskStatus.QUEUED
        ).save()
        site_two = await self.simple_site(last_run_status=TaskStatus.IN_PROGRESS).save()
        site_three = await self.simple_site().save()
        await self.simple_scrape(site_one).save()
        await self.simple_scrape(site_two).save()
        scrape_one = await self.simple_scrape(site_three).save()

        res = await runBulkByType("cancel-active", MockLogger, User)
        assert res == {"status": True, "canceled_scrapes": 2}
        canceled_scrapes = await SiteScrapeTask.find(
            {"status": TaskStatus.CANCELING}
        ).to_list()
        assert len(canceled_scrapes) == 2
        active_scrapes = await SiteScrapeTask.find(
            {"status": TaskStatus.QUEUED}
        ).to_list()
        assert len(active_scrapes) == 1
        assert active_scrapes[0].id == scrape_one.id

    @pytest.mark.asyncio
    async def test_cancel_no_scrapes(self):
        site_one = await self.simple_site().save()
        scrape_one = await self.simple_scrape(site_one).save()

        res = await runBulkByType("cancel-active", MockLogger, User)
        assert res == {"status": True, "canceled_scrapes": 0}
        scrapes = await SiteScrapeTask.find({"status": TaskStatus.CANCELED}).to_list()
        assert len(scrapes) == 0
