from random import random

import pytest
import pytest_asyncio

from backend.app.routes.document_family import read_document_families
from backend.app.routes.table_query import TableFilterInfo, TableSortInfo
from backend.common.core.enums import CollectionMethod, DocumentType, SiteStatus
from backend.common.db.init import init_db
from backend.common.models.document_family import DocumentFamily, PayerInfo
from backend.common.models.site import BaseUrl, HttpUrl, ScrapeMethodConfiguration, Site
from backend.common.models.user import User


@pytest_asyncio.fixture(autouse=True)
async def before_each_test():
    random_name = str(random())
    await init_db(mock=True, database_name=random_name)


@pytest_asyncio.fixture()
@pytest.mark.asyncio()
async def user():
    user = User(
        id="62e7c6647e2a94f469d57f34",
        email="example@me.com",
        full_name="John Doe",
        hashed_password="example",
    )
    await user.save()

    return user


class MockLogger:
    async def background_log_change(
        self, current_user: User, document_family: DocumentFamily, action: str
    ):
        assert current_user.id is not None
        assert type(action) == str
        return None


@pytest_asyncio.fixture()
async def logger():
    return MockLogger()


def simple_site(
    disabled=False,
    base_urls=[BaseUrl(url=HttpUrl("https://www.example.com/", scheme="https"), status="ACTIVE")],
    collection_method=CollectionMethod.Automated,
    collection_hold=None,
    status=SiteStatus.ONLINE,
    last_run_status=None,
) -> Site:
    return Site(
        name="Test",
        collection_method=collection_method,
        collection_hold=collection_hold,
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


def create_document_family(
    site: Site,
    document_type=DocumentType.AuthorizationPolicy,
    description="Example description",
    relevance=[],
    payer_info=PayerInfo(),
    field_groups=[],
    legacy_relevance=[],
    disabled=False,
) -> DocumentFamily:
    return DocumentFamily(
        name="Test Family",
        document_type=document_type,
        description=description,
        site_id=site.id,
        relevance=relevance,
        payer_info=payer_info,
        field_groups=field_groups,
        legacy_relevance=legacy_relevance,
        disabled=disabled,
    )


class TestReadDocumentFamilies:
    @pytest.mark.asyncio
    async def test_read_all_document_families(self):
        limit = 50
        filters = [
            TableFilterInfo(name="document_type", operator="eq", type="select", value=None),
            TableFilterInfo(name="name", operator="contains", type="string", value=None),
        ]
        sorts = [TableSortInfo(name="name", dir=-1)]
        skip = 0
        site_one = await simple_site().save()
        await create_document_family(site_one).save()
        await create_document_family(site_one).save()
        await create_document_family(site_one).save()
        await create_document_family(site_one).save()
        await create_document_family(site_one).save()
        docFamilies = await read_document_families(limit, skip, sorts, filters)
        assert docFamilies.total == 5
