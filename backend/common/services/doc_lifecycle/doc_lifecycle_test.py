from datetime import datetime, timedelta
from random import random

import pytest_asyncio
from beanie import PydanticObjectId

from backend.common.core.enums import ApprovalStatus, DocumentType
from backend.common.db.init import init_db
from backend.common.models.content_extraction_task import ContentExtractionTask, DeltaStats
from backend.common.models.doc_document import DocDocument
from backend.common.models.document_family import DocumentFamily
from backend.common.models.shared import DocDocumentLocation
from backend.common.models.site import Site
from backend.common.services.doc_lifecycle.doc_lifecycle import DocLifecycleService


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


class BasicDocFamily(DocumentFamily):
    name: str = ""
    document_type: str = DocumentType.AuthorizationPolicy
    site_id: PydanticObjectId | None = PydanticObjectId()


async def test_doc_type():
    service = DocLifecycleService()
    doc = BasicDoc(document_type=DocumentType.AuthorizationPolicy, doc_type_confidence=0.6)
    site = Site(name="Name", doc_type_threshold=0.7)

    # Unlineaged, use confidence only
    assert service.doc_type_needs_review(doc, None, site)

    site.doc_type_threshold = 0.5
    assert not service.doc_type_needs_review(doc, None, site)

    # Lineaged, require review if doc types differ
    prev_doc = BasicDoc(document_type=DocumentType.Formulary, doc_type_confidence=0.6)
    assert service.doc_type_needs_review(doc, prev_doc, site)

    prev_doc.document_type = DocumentType.AuthorizationPolicy
    assert not service.doc_type_needs_review(doc, prev_doc, site)


async def test_lineage():
    service = DocLifecycleService()
    doc = BasicDoc()

    # Unlineaged, use far dates only
    doc.final_effective_date = datetime.now() + timedelta(weeks=100)
    assert service.effective_date_needs_review(doc, None)

    doc.final_effective_date = datetime.now() - timedelta(weeks=1000)
    assert service.effective_date_needs_review(doc, None)

    doc.final_effective_date = datetime.now() + timedelta(weeks=12)
    assert not service.effective_date_needs_review(doc, None)

    doc.final_effective_date = datetime.now() - timedelta(weeks=100)
    assert not service.effective_date_needs_review(doc, None)

    # Lineaged, require new effective date after old
    prev_doc = BasicDoc(final_effective_date=datetime.now())

    doc.final_effective_date = datetime.now() - timedelta(weeks=1)
    assert service.effective_date_needs_review(doc, prev_doc)

    doc.final_effective_date = datetime.now() + timedelta(weeks=1)
    assert not service.effective_date_needs_review(doc, prev_doc)


async def test_assess_classification():
    service = DocLifecycleService()
    prev_doc = BasicDoc(
        document_type=DocumentType.AuthorizationPolicy,
        doc_type_confidence=0.9,
        final_effective_date=datetime.now(),
    )
    await prev_doc.save()
    doc = BasicDoc(
        previous_doc_doc_id=prev_doc.id,
        document_type=DocumentType.AuthorizationPolicy,
        doc_type_confidence=0.9,
        final_effective_date=datetime.now() + timedelta(weeks=1),
    )
    site = Site(name="site", doc_type_threshold=0.7)

    status, _ = await service.assess_classification_status(doc, site)
    assert status == ApprovalStatus.APPROVED

    doc.classification_status = ApprovalStatus.PENDING
    doc.doc_type_confidence = 0.2
    doc.final_effective_date = datetime.now() + timedelta(weeks=100)
    doc.previous_doc_doc_id = None
    await service.assess_classification_status(doc, site)
    assert doc.classification_hold_info == ["DOC_TYPE", "EFFECTIVE_DATE", "LINEAGE"]


async def test_assess_document_family():
    service = DocLifecycleService()
    doc = BasicDoc(locations=[BasicLocation(document_family_id=PydanticObjectId())])
    status, _ = service.assess_doc_family_status(doc)
    assert status == ApprovalStatus.APPROVED

    doc.locations.append(BasicLocation())

    status, _ = service.assess_doc_family_status(doc)
    assert status == ApprovalStatus.QUEUED


async def test_content_extraction_needs_review():
    service = DocLifecycleService()
    task = ContentExtractionTask(queued_time=datetime.now(), delta=DeltaStats(total=100))
    task.delta.removed = 100
    assert service.extraction_delta_needs_review(task)

    task.delta.removed = 4
    assert not service.extraction_delta_needs_review(task)


async def test_assess_content_extraction():
    service = DocLifecycleService()
    site = Site(id=PydanticObjectId(), name="s")
    doc_family = BasicDocFamily(site_id=site.id, legacy_relevance=["PAR"])
    await doc_family.save()
    doc = BasicDoc(locations=[BasicLocation(site_id=site.id, document_family_id=doc_family.id)])

    # No extraction needed, nothing to do
    status, _ = await service.assess_content_extraction_status(doc, site)
    assert status == ApprovalStatus.APPROVED

    # No translation set but selected for automated editor extraction
    doc.content_extraction_status = ApprovalStatus.PENDING
    doc_family.legacy_relevance.append("EDITOR_AUTOMATED")
    await doc_family.save()
    status, _ = await service.assess_content_extraction_status(doc, site)
    assert doc.extraction_hold_info == ["NO_TRANSLATION"]

    # Translation is set but no content_extraction_task_id means translation in progress, do nothing
    doc.content_extraction_status = ApprovalStatus.PENDING
    doc.translation_id = PydanticObjectId()
    status, _ = await service.assess_content_extraction_status(doc, site)
    assert status == ApprovalStatus.PENDING

    # Translation is set but no content_extraction_task_id means translation in progress, do nothing
    extraction = ContentExtractionTask(queued_time=datetime.now(), delta=DeltaStats(total=100))
    extraction.delta.removed = 10
    await extraction.save()
    doc.content_extraction_task_id = extraction.id
    status, _ = await service.assess_content_extraction_status(doc, site)
    assert doc.extraction_hold_info == ["EXTRACT_DELTA"]

    extraction.delta.removed = 4
    await extraction.save()
    doc.content_extraction_status = ApprovalStatus.PENDING
    status, _ = await service.assess_content_extraction_status(doc, site)
    assert status == ApprovalStatus.APPROVED and doc.extraction_hold_info == []


async def test_intermediate_statuses():
    service = DocLifecycleService()
    site = Site(id=PydanticObjectId(), name="s", doc_type_threshold=0.8)
    doc_family = BasicDocFamily(site_id=site.id, legacy_relevance=["EDITOR_AUTOMATED"])
    await doc_family.save()
    extraction = ContentExtractionTask(queued_time=datetime.now(), delta=DeltaStats(total=100))
    await extraction.save()
    doc = BasicDoc(locations=[BasicLocation(site_id=site.id)])

    fully_approved, _ = await service.assess_intermediate_statuses(doc, site)
    assert not fully_approved

    prev_doc = BasicDoc(
        document_type=DocumentType.AuthorizationPolicy,
        final_effective_date=datetime.now() - timedelta(weeks=1),
    )
    await prev_doc.save()
    doc.document_type = DocumentType.AuthorizationPolicy
    doc.doc_type_confidence = 0.9
    doc.previous_doc_doc_id = prev_doc.id
    doc.final_effective_date = datetime.now()
    doc.classification_status = ApprovalStatus.PENDING

    fully_approved, _ = await service.assess_intermediate_statuses(doc, site)
    assert doc.classification_status == ApprovalStatus.APPROVED
    assert not fully_approved

    doc.family_status = ApprovalStatus.PENDING
    doc.locations[0].document_family_id = doc_family.id

    fully_approved, _ = await service.assess_intermediate_statuses(doc, site)
    assert doc.family_status == ApprovalStatus.APPROVED
    assert not fully_approved

    doc.content_extraction_status = ApprovalStatus.PENDING
    doc.translation_id = PydanticObjectId()
    doc.content_extraction_task_id = extraction.id

    fully_approved, _ = await service.assess_intermediate_statuses(doc, site)
    assert doc.content_extraction_status == ApprovalStatus.APPROVED
    assert fully_approved
