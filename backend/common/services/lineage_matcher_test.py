from random import random

import pytest_asyncio

from backend.common.db.init import init_db
from backend.common.models.lineage import DocumentAnalysis
from backend.common.services.lineage_matcher import LineageMatcher

# @pytest_asyncio.fixture(autouse=True)
# async def before_each_test():
#     random_name = str(random())
#     await init_db(mock=True, database_name=random_name)
