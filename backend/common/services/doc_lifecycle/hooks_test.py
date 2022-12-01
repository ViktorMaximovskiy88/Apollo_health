from random import random

import pytest_asyncio
from beanie import PydanticObjectId

from backend.common.core.enums import DocumentType
from backend.common.db.init import init_db
from backend.common.models.doc_document import DocDocument, DocDocumentLocation
from backend.common.models.document_family import DocumentFamily
from backend.common.models.payer_family import PayerFamily
from backend.common.services.doc_lifecycle.hooks import (
    ChangeInfo,
    update_document_family_counts,
    update_payer_family_counts,
)


@pytest_asyncio.fixture(autouse=True)
async def before_each_test():
    random_name = str(random())
    await init_db(mock=True, database_name=random_name)


class BasicDoc(DocDocument):
    name: str = "d"
    retrieved_document_id: PydanticObjectId = PydanticObjectId()
    checksum: str = "d"


class BasicLocation(DocDocumentLocation):
    base_url: str = ""
    url: str = ""
    site_id: PydanticObjectId | None = PydanticObjectId()


async def test_update_payer_family_counts_added():
    pf = PayerFamily(name="pf1")
    await pf.save()
    change_info = ChangeInfo(old_payer_family_ids=[])
    doc = BasicDoc(locations=[BasicLocation(payer_family_id=pf.id)])

    await update_payer_family_counts(doc, change_info)

    pf = await PayerFamily.find_one({"_id": pf.id})
    assert pf and pf.doc_doc_count == 1

    change_info = ChangeInfo(old_payer_family_ids=[pf.id])
    doc = BasicDoc(locations=[BasicLocation(payer_family_id=None)])

    await update_payer_family_counts(doc, change_info)

    pf = await PayerFamily.find_one({"_id": pf.id})
    assert pf and pf.doc_doc_count == 0


async def test_update_document_family_counts_added():
    df = DocumentFamily(name="df1", document_type=DocumentType.Formulary)
    await df.save()

    await update_document_family_counts(new_document_family_id=df.id, old_document_family_id=None)

    df = await DocumentFamily.find_one({"_id": df.id})
    assert df and df.doc_doc_count == 1

    await update_document_family_counts(old_document_family_id=df.id, new_document_family_id=None)
    df = await DocumentFamily.find_one({"_id": df.id})
    assert df and df.doc_doc_count == 0
