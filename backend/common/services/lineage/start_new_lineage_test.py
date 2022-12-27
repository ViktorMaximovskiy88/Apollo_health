from random import random

import pytest
import pytest_asyncio
from beanie import PydanticObjectId

from backend.common.db.init import init_db
from backend.common.models.doc_document import DocDocument
from backend.common.services.lineage.start_new_lineage import start_new_lineage


class BasicDoc(DocDocument):
    retrieved_document_id: PydanticObjectId = PydanticObjectId()
    checksum: str = "d"
    pipeline_stages: list = []


@pytest_asyncio.fixture(autouse=True)
async def before_each_test():
    await init_db(mock=True, database_name=str(random()))
    l1 = PydanticObjectId()
    a = BasicDoc(name="A", id=PydanticObjectId(), lineage_id=l1)
    b = BasicDoc(name="B", id=PydanticObjectId(), previous_doc_doc_id=a.id, lineage_id=l1)
    c = BasicDoc(
        name="C",
        id=PydanticObjectId(),
        previous_doc_doc_id=b.id,
        lineage_id=l1,
        is_current_version=True,
    )

    for doc in [a, b, c]:
        await doc.insert()


# L: A -> B -> C
# A -> Start new lineage
# include_later_documents: False
@pytest.mark.asyncio
async def test_case_1():
    a = await BasicDoc.find_one({"name": "A"})
    if not a:
        return
    assert a.previous_doc_doc_id is None
    await start_new_lineage(
        updating_doc_doc=a, old_prev_doc_doc_id=None, include_later_documents=False
    )

    a = await BasicDoc.find_one({"name": "A"})
    b = await BasicDoc.find_one({"name": "B"})
    c = await BasicDoc.find_one({"name": "C"})
    if not (a and b and c):
        return

    assert a.is_current_version
    assert not b.is_current_version
    assert c.is_current_version

    assert b.lineage_id == c.lineage_id
    assert a.lineage_id != b.lineage_id

    assert c.previous_doc_doc_id == b.id
    assert a.previous_doc_doc_id is None
    assert b.previous_doc_doc_id is None


# L: A -> B -> C
# B -> Start new lineage
# include_later_documents: False
@pytest.mark.asyncio
async def test_case_2():
    b = await BasicDoc.find_one({"name": "B"})
    if not b:
        return
    old_prev = b.previous_doc_doc_id
    b.previous_doc_doc_id = None
    await start_new_lineage(
        updating_doc_doc=b, old_prev_doc_doc_id=old_prev, include_later_documents=False
    )

    a = await BasicDoc.find_one({"name": "A"})
    b = await BasicDoc.find_one({"name": "B"})
    c = await BasicDoc.find_one({"name": "C"})
    if not (a and b and c):
        return

    assert not a.is_current_version
    assert b.is_current_version
    assert c.is_current_version

    assert a.lineage_id == c.lineage_id
    assert a.lineage_id != b.lineage_id

    assert c.previous_doc_doc_id == a.id
    assert a.previous_doc_doc_id is None
    assert b.previous_doc_doc_id is None


# L: A -> B -> C
# C -> Start new lineage
# include_later_documents: False
@pytest.mark.asyncio
async def test_case_3():
    c = await BasicDoc.find_one({"name": "C"})
    if not c:
        return
    old_prev = c.previous_doc_doc_id
    c.previous_doc_doc_id = None
    await start_new_lineage(
        updating_doc_doc=c, old_prev_doc_doc_id=old_prev, include_later_documents=False
    )

    a = await BasicDoc.find_one({"name": "A"})
    b = await BasicDoc.find_one({"name": "B"})
    c = await BasicDoc.find_one({"name": "C"})
    if not (a and b and c):
        return

    assert not a.is_current_version
    assert b.is_current_version
    assert c.is_current_version

    assert a.lineage_id == b.lineage_id
    assert a.lineage_id != c.lineage_id

    assert b.previous_doc_doc_id == a.id
    assert a.previous_doc_doc_id is None
    assert c.previous_doc_doc_id is None


# L: A -> B -> C
# A -> Start new lineage
# include_later_documents: True
@pytest.mark.asyncio
async def test_case_4():
    a = await BasicDoc.find_one({"name": "A"})
    if not a:
        return
    assert a.previous_doc_doc_id is None
    await start_new_lineage(
        updating_doc_doc=a, old_prev_doc_doc_id=None, include_later_documents=True
    )

    a = await BasicDoc.find_one({"name": "A"})
    b = await BasicDoc.find_one({"name": "B"})
    c = await BasicDoc.find_one({"name": "C"})
    if not (a and b and c):
        return

    assert not a.is_current_version
    assert not b.is_current_version
    assert c.is_current_version

    assert a.lineage_id == b.lineage_id == c.lineage_id

    assert a.previous_doc_doc_id is None
    assert b.previous_doc_doc_id == a.id
    assert c.previous_doc_doc_id == b.id


# L: A -> B -> C
# B -> Start new lineage
# include_later_documents: True
@pytest.mark.asyncio
async def test_case_5():
    b = await BasicDoc.find_one({"name": "B"})
    if not b:
        return
    old_prev = b.previous_doc_doc_id
    b.previous_doc_doc_id = None
    await start_new_lineage(
        updating_doc_doc=b, old_prev_doc_doc_id=old_prev, include_later_documents=True
    )

    a = await BasicDoc.find_one({"name": "A"})
    b = await BasicDoc.find_one({"name": "B"})
    c = await BasicDoc.find_one({"name": "C"})
    if not (a and b and c):
        return

    assert a.is_current_version
    assert not b.is_current_version
    assert c.is_current_version

    assert b.lineage_id == c.lineage_id
    assert a.lineage_id != b.lineage_id

    assert a.previous_doc_doc_id is None
    assert b.previous_doc_doc_id is None
    assert c.previous_doc_doc_id == b.id


# L: A -> B -> C
# C -> Start new lineage
# include_later_documents: True
@pytest.mark.asyncio
async def test_case_6():
    b = await BasicDoc.find_one({"name": "B"})
    c = await BasicDoc.find_one({"name": "C"})
    if not c:
        return
    old_prev = c.previous_doc_doc_id
    c.previous_doc_doc_id = None
    await start_new_lineage(
        updating_doc_doc=c, old_prev_doc_doc_id=old_prev, include_later_documents=True
    )

    a = await BasicDoc.find_one({"name": "A"})
    b = await BasicDoc.find_one({"name": "B"})
    c = await BasicDoc.find_one({"name": "C"})
    if not (a and b and c):
        return

    assert not a.is_current_version
    assert b.is_current_version
    assert c.is_current_version

    assert a.lineage_id == b.lineage_id
    assert a.lineage_id != c.lineage_id

    assert a.previous_doc_doc_id is None
    assert b.previous_doc_doc_id == a.id
    assert c.previous_doc_doc_id is None
