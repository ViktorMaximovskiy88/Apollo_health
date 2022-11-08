#   C -> Previous Version E
#   C -> Not Current Version
#   C -> Lineage becomes L2
#   B -> Current Version
#   F -> Previous Version C
# B move to F
#   B -> Previous Version F
#   B -> Lineage L2
#   F -> Not Current Version
#   A -> Current Version
# B move to E

from random import random

import pytest
import pytest_asyncio
from beanie import PydanticObjectId

from backend.common.db.init import init_db
from backend.common.models.doc_document import DocDocument
from backend.common.services.lineage.update_prev_document import update_lineage


class BasicDoc(DocDocument):
    retrieved_document_id: PydanticObjectId = PydanticObjectId()
    checksum: str = "d"


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

    l2 = PydanticObjectId()
    d = BasicDoc(name="D", id=PydanticObjectId(), lineage_id=l2)
    e = BasicDoc(name="E", id=PydanticObjectId(), previous_doc_doc_id=d.id, lineage_id=l2)
    f = BasicDoc(
        name="F",
        id=PydanticObjectId(),
        previous_doc_doc_id=e.id,
        lineage_id=l2,
        is_current_version=True,
    )
    for doc in [a, b, c, d, e, f]:
        await doc.insert()


# L1: A -> B -> C
# L2: D -> E -> F
# C move to F
@pytest.mark.asyncio
async def test_case_1():
    c = await BasicDoc.find_one({"name": "C"})
    f = await BasicDoc.find_one({"name": "F"})
    if not c or not f:
        return
    old_prev = c.previous_doc_doc_id
    c.previous_doc_doc_id = f.id
    await update_lineage(c, old_prev, f.id)

    b = await BasicDoc.find_one({"name": "B"})
    c = await BasicDoc.find_one({"name": "C"})
    f = await BasicDoc.find_one({"name": "F"})
    if not (b and c and f):
        return

    assert b.is_current_version
    assert c.lineage_id == f.lineage_id
    assert c.previous_doc_doc_id == f.id
    assert c.is_current_version
    assert not f.is_current_version


# L1: A -> B -> C
# L2: D -> E -> F
# C -> Previous Version E
@pytest.mark.asyncio
async def test_case_2():
    c = await BasicDoc.find_one({"name": "C"})
    e = await BasicDoc.find_one({"name": "E"})
    if not c or not e:
        return
    old_prev = c.previous_doc_doc_id
    c.previous_doc_doc_id = e.id
    await update_lineage(c, old_prev, e.id)

    b = await BasicDoc.find_one({"name": "B"})
    c = await BasicDoc.find_one({"name": "C"})
    e = await BasicDoc.find_one({"name": "E"})
    f = await BasicDoc.find_one({"name": "F"})
    if not (b and c and f and e):
        return

    assert b.is_current_version
    assert c.lineage_id == f.lineage_id
    assert c.previous_doc_doc_id == e.id
    assert f.previous_doc_doc_id == c.id
    assert not c.is_current_version


# L1: A -> B -> C
# L2: D -> E -> F
# B -> Previous Version F
@pytest.mark.asyncio
async def test_case_3():
    b = await BasicDoc.find_one({"name": "B"})
    f = await BasicDoc.find_one({"name": "F"})
    if not b or not f:
        return
    old_prev = b.previous_doc_doc_id
    b.previous_doc_doc_id = f.id
    await update_lineage(b, old_prev, f.id)

    a = await BasicDoc.find_one({"name": "A"})
    b = await BasicDoc.find_one({"name": "B"})
    c = await BasicDoc.find_one({"name": "C"})
    e = await BasicDoc.find_one({"name": "E"})
    f = await BasicDoc.find_one({"name": "F"})
    if not (a and b and c and f and e):
        return

    assert a.is_current_version

    assert b.lineage_id == f.lineage_id
    assert c.lineage_id == f.lineage_id

    assert b.previous_doc_doc_id == f.id

    assert c.is_current_version
    assert not f.is_current_version


# L1: A -> B -> C
# L2: D -> E -> F
# B -> Previous Version E
@pytest.mark.asyncio
async def test_case_4():
    b = await BasicDoc.find_one({"name": "B"})
    e = await BasicDoc.find_one({"name": "E"})
    if not b or not e:
        return
    old_prev = b.previous_doc_doc_id
    b.previous_doc_doc_id = e.id
    await update_lineage(b, old_prev, e.id)

    a = await BasicDoc.find_one({"name": "A"})
    b = await BasicDoc.find_one({"name": "B"})
    c = await BasicDoc.find_one({"name": "C"})
    e = await BasicDoc.find_one({"name": "E"})
    f = await BasicDoc.find_one({"name": "F"})
    if not (a and b and c and f and e):
        return

    assert a.is_current_version

    assert b.lineage_id == f.lineage_id
    assert c.lineage_id == f.lineage_id

    assert b.previous_doc_doc_id == e.id

    assert not c.is_current_version
    assert f.is_current_version
    assert f.previous_doc_doc_id == c.id


# L1: A -> B -> C
# L2: D -> E -> F
# A -> Previous Version F
@pytest.mark.asyncio
async def test_case_5():
    a = await BasicDoc.find_one({"name": "A"})
    f = await BasicDoc.find_one({"name": "F"})
    if not a or not f:
        return
    old_prev = a.previous_doc_doc_id
    a.previous_doc_doc_id = f.id
    await update_lineage(a, old_prev, f.id)

    a = await BasicDoc.find_one({"name": "A"})
    b = await BasicDoc.find_one({"name": "B"})
    c = await BasicDoc.find_one({"name": "C"})
    e = await BasicDoc.find_one({"name": "E"})
    f = await BasicDoc.find_one({"name": "F"})
    if not (a and b and c and f and e):
        return

    assert not f.is_current_version
    assert c.is_current_version

    assert a.lineage_id == f.lineage_id
    assert b.lineage_id == f.lineage_id
    assert c.lineage_id == f.lineage_id

    assert a.previous_doc_doc_id == f.id
    assert b.previous_doc_doc_id == a.id
    assert c.previous_doc_doc_id == b.id
