from datetime import datetime
from random import random

import pytest
import pytest_asyncio
from beanie import PydanticObjectId
from pydantic import HttpUrl

from backend.app.routes.table_query import (
    TableFilterInfo,
    TableSortInfo,
    _prepare_table_query,
    transform_value,
)
from backend.common.core.enums import ApprovalStatus, CollectionMethod, ScrapeMethod, SiteStatus
from backend.common.db.init import init_db
from backend.common.models.doc_document import DocDocument
from backend.common.models.document import RetrievedDocument
from backend.common.models.document_family import DocumentFamily
from backend.common.models.shared import DocDocumentLocation, RetrievedDocumentLocation
from backend.common.models.site import BaseUrl, ScrapeMethodConfiguration, Site
from backend.common.models.user import User


@pytest_asyncio.fixture(autouse=True)
async def before_each_test():
    random_name = str(random())
    await init_db(mock=True, database_name=random_name)


@pytest_asyncio.fixture()
@pytest.mark.asyncio()
async def user():
    user = User(
        id=PydanticObjectId(),
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
    status=SiteStatus.ONLINE,
    last_run_status=None,
) -> Site:
    return Site(
        name="Test",
        collection_method=collection_method,
        scrape_method=ScrapeMethod.Simple,
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


def simple_ret_doc(site: Site) -> RetrievedDocument:
    doc = RetrievedDocument(
        name="test",
        checksum="test",
        text_checksum="test",
        first_collected_date=datetime.now(),
        last_collected_date=datetime.now(),
        doc_type_match=None,
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
    )
    return doc


def simple_doc_doc(site: Site, ret_doc: RetrievedDocument, i: int) -> DocDocument:
    doc = DocDocument(
        name=f"test{i}",
        checksum=f"test{i}",
        text_checksum=f"test{i}",
        document_type="Treatment Request Form",
        first_collected_date=datetime.now(),
        retrieved_document_id=ret_doc.id,
        family_status=ApprovalStatus.APPROVED,
        last_collected_date=datetime.now(),
        last_updated_date=datetime.now(),
        document_family_id=PydanticObjectId(),
        classification_status=ApprovalStatus.APPROVED,
        locations=[
            DocDocumentLocation(
                site_id=site.id,  # type: ignore
                first_collected_date=datetime.now(),
                last_collected_date=datetime.now(),
                url="https://www.example.com/doc",
                base_url="https://www.example.com/",
                link_text="",
                closest_heading="",
                siblings_text=None,
            )
        ],
    )
    return doc


async def populate_db():

    await init_db(mock=True)
    site = simple_site()
    await site.save()
    ret_doc = simple_ret_doc(site)
    await ret_doc.save()
    docs: list[RetrievedDocument] = []
    for i in range(10):
        doc = simple_doc_doc(site, ret_doc, i)
        await doc.save()
    return docs


def test_prepare_table_query_different_value_type():
    filters = [
        TableFilterInfo(name="document_type", operator="notinlist", type="select", value=None),
        TableFilterInfo(
            name="document_type", operator="notinlist", type="select", value=["term1", "term2"]
        ),
        TableFilterInfo(name="document_type", operator="neq", type="select", value=""),
        TableFilterInfo(name="document_type", operator="neq", type="select", value=None),
    ]
    sorts = [TableSortInfo(name="name", dir=-1)]
    docFamilies = _prepare_table_query(sorts, filters)
    assert docFamilies == (
        [
            {"document_type": {"$nin": []}},
            {"document_type": {"$nin": ["term1", "term2"]}},
            {"document_type": {"$ne": None}},
            {"document_type": {"$ne": None}},
        ],
        [("name", -1)],
    )


def test_prepare_table_query_sorts():
    filters = [
        TableFilterInfo(name="document_type", operator="notinlist", type="select", value=None),
    ]
    sorts = [TableSortInfo(name="name", dir=-1), TableSortInfo(name="name2", dir=1)]
    match, sort_by = _prepare_table_query(sorts, filters)
    assert sort_by == [("name", -1), ("name2", 1)]


def test_prepare_table_query_no_filter_value_and_operator_in_list():
    filters = [
        TableFilterInfo(name="document_type", operator="empty", type="select", value=None),
        TableFilterInfo(name="document_type", operator="notEmpty", type="select", value=None),
        TableFilterInfo(name="document_type", operator="leq", type="select", value=None),
        TableFilterInfo(name="document_type", operator="neq", type="select", value=None),
        TableFilterInfo(name="document_type", operator="notinlist", type="select", value=None),
    ]
    sorts = [TableSortInfo(name="name", dir=-1)]
    match, sort_by = _prepare_table_query(sorts, filters)
    assert match == [
        {"document_type": {"$in": [None, ""]}},
        {"document_type": {"$exists": True, "$nin": [None, ""]}},
        {"document_type": ""},
        {"document_type": {"$ne": None}},
        {"document_type": {"$nin": []}},
    ]


# ["empty", "notEmpty", "leq","notinlist","neq"]
def test_prepare_table_query_no_filter_value_and_operator_not_in_list():
    filters = [
        TableFilterInfo(name="document_type", operator="textcontains", type="select", value=None),
    ]
    sorts = [TableSortInfo(name="name", dir=-1)]
    match, sort_by = _prepare_table_query(sorts, filters)
    assert match == []


def test_prepare_table_query_value_is_None():
    filters = [
        TableFilterInfo(name="document_type", operator="empty", type="select", value=None),
    ]
    sorts = [TableSortInfo(name="name", dir=-1)]
    match, sort_by = _prepare_table_query(sorts, filters)
    assert match == [{"document_type": {"$in": [None, ""]}}]


def test_transform_value_boolean():
    value1 = "True"
    value2 = "False"
    type = "boolean"
    resp1 = transform_value(value1, type)
    assert resp1 is True
    resp2 = transform_value(value2, type)
    assert resp2 is False


def test_transform_value_date_number():
    value = "2023-02-08"
    value1 = "1"
    type = "date"
    type1 = "number"
    resp = transform_value(value, type)
    resp1 = transform_value(value1, type1)
    assert resp == datetime(2023, 2, 8)
    assert resp1 == 1
