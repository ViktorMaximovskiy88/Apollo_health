from random import random

import pytest
import pytest_asyncio
from beanie import PydanticObjectId

from backend.app.routes.table_query import TableFilterInfo, TableSortInfo, _prepare_table_query
from backend.common.db.init import init_db
from backend.common.models.document_family import DocumentFamily
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


def test_prepare_table_query():
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
