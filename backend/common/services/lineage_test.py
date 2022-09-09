import logging

import pytest

from backend.common.db.init import init_db
from backend.common.services.lineage import LineageService


@pytest.mark.asyncio()
async def test_this():
    await init_db()
    lineage_service = LineageService(log=logging)
    await lineage_service.process_lineage_for_sites()
