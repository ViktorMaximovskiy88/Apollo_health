import pytest

from backend.common.db.init import init_db


@pytest.mark.asyncio()
async def test_this():
    await init_db()
