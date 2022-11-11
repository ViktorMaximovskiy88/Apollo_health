from datetime import datetime
from random import random

import pytest
import pytest_asyncio
from beanie import PydanticObjectId

from backend.common.core.enums import TaskStatus
from backend.common.db.init import init_db
from backend.common.models.content_extraction_task import ContentExtractionTask
from backend.common.models.doc_document import DocDocument
from backend.common.models.translation_config import TranslationConfig
from backend.parseworker.extractor import TableContentExtractor


class BasicDoc(DocDocument):
    retrieved_document_id: PydanticObjectId = PydanticObjectId()
    checksum: str = ""


@pytest_asyncio.fixture(autouse=True)
async def before_each_test():
    await init_db(mock=True, database_name=str(random()))
    taska = await ContentExtractionTask(
        queued_time=datetime.now(), status=TaskStatus.FINISHED
    ).save()
    taskb = await ContentExtractionTask(
        queued_time=datetime.now(), status=TaskStatus.FINISHED
    ).save()
    taskc = await ContentExtractionTask(
        queued_time=datetime.now(), status=TaskStatus.FINISHED
    ).save()
    a = await BasicDoc(name="A", content_extraction_task_id=taska.id).save()
    b = await BasicDoc(
        name="B", previous_doc_doc_id=a.id, content_extraction_task_id=taskb.id
    ).save()
    await BasicDoc(name="C", previous_doc_doc_id=b.id, content_extraction_task_id=taskc.id).save()


async def get_docs_tasks():
    a = await DocDocument.find_one({"name": "A"})
    b = await DocDocument.find_one({"name": "B"})
    c = await DocDocument.find_one({"name": "C"})
    if not (a and b and c):
        raise Exception("Unreacable")
    if not (
        a.content_extraction_task_id
        and b.content_extraction_task_id
        and c.content_extraction_task_id
    ):
        raise Exception("Unreacable")
    taska = await ContentExtractionTask.get(a.content_extraction_task_id)
    taskb = await ContentExtractionTask.get(b.content_extraction_task_id)
    taskc = await ContentExtractionTask.get(c.content_extraction_task_id)
    if not (taska and taskb and taskc):
        raise Exception("Unreacable")
    return a, b, c, taska, taskb, taskc


@pytest.mark.asyncio()
async def test_calculate_delta():
    a, b, c, taska, taskb, taskc = await get_docs_tasks()
    config = TranslationConfig()
    modified = await TableContentExtractor(a, config).calculate_delta(taska)
    assert modified == [taskb.id]

    modified = await TableContentExtractor(b, config).calculate_delta(taskb)
    assert modified == [taskb.id, taskc.id]

    modified = await TableContentExtractor(c, config).calculate_delta(taskc)
    assert modified == [taskc.id]


@pytest.mark.asyncio()
async def test_calculate_delta_2():
    a, b, c, taska, taskb, taskc = await get_docs_tasks()
    a.content_extraction_task_id = None
    await a.save()

    config = TranslationConfig()
    modified = await TableContentExtractor(b, config).calculate_delta(taskb)
    assert modified == [taskc.id]

    c.content_extraction_task_id = None
    await c.save()

    modified = await TableContentExtractor(b, config).calculate_delta(taskb)
    assert modified == []
