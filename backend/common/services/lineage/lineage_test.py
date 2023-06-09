import logging
from datetime import datetime, timezone
from random import random

import pytest
from beanie import PydanticObjectId

from backend.common.db.init import init_db
from backend.common.models.doc_document import DocDocument
from backend.common.models.document import RetrievedDocument
from backend.common.models.shared import (
    DocDocumentLocation,
    IndicationTag,
    RetrievedDocumentLocation,
    TherapyTag,
)
from backend.common.services.lineage.core import LineageService
from backend.common.test.test_utils import mock_s3_client  # noqa

site_id_a = PydanticObjectId("00000000000000000000000a")
site_id_b = PydanticObjectId("00000000000000000000000b")


async def load_retrieved_docs() -> list[RetrievedDocument]:
    docs: list[RetrievedDocument] = []
    # exact focus match, 10% file size same doc type, doc_type conf > X
    docs.append(
        RetrievedDocument(
            site_id=site_id_a,
            name="Tykerb (659616) May 2022",
            checksum="0000000000000000000000000000000A",
            effective_date=datetime(2022, 5, 1, tzinfo=timezone.utc),
            document_type="Formulary",
            doc_type_confidence=1,
            therapy_tags=[TherapyTag(text="Tykerb", name="Tykerb", code="659616", focus=1)],
            indication_tags=[IndicationTag(text="TDAP", code=155, focus=False)],
            file_size=1500000,
            locations=[
                RetrievedDocumentLocation(
                    site_id=site_id_a,
                    url="https://www.example.com/formularies/ga-2022-05-tykerb.pdf",
                    link_text="Tykerb",
                    closest_heading="Formularies",
                    base_url="https://www.example.com/formularies/",
                    context_metadata={
                        "link_text": "Tykerb",
                        "element_id": None,
                        "closest_heading": "Formularies",
                        "siblings_text": None,
                        "resource_value": "https://www.example.com/formularies/ga-2022-05-tykerb.pdf",
                        "base_url": "https://www.example.com/formularies/",
                        "playbook_context": None,
                    },
                )
            ],
        )
    )

    docs.append(
        RetrievedDocument(
            site_id=site_id_a,
            name="Tykerb (659616) June 2022",
            checksum="0000000000000000000000000000000B",
            effective_date=datetime(2022, 6, 1, tzinfo=timezone.utc),
            document_type="Formulary",
            doc_type_confidence=1,
            therapy_tags=[TherapyTag(text="Tykerb", name="Tykerb", code="659616", focus=1)],
            indication_tags=[IndicationTag(text="TDAP", code=155, focus=False)],
            file_size=1600000,
            locations=[
                RetrievedDocumentLocation(
                    site_id=site_id_a,
                    url="https://www.example.com/formularies/ga-2022-06-tykerb.pdf",
                    link_text="Tykerb",
                    closest_heading="Formularies",
                    base_url="https://www.example.com/formularies/",
                    context_metadata={
                        "link_text": "Tykerb",
                        "element_id": None,
                        "closest_heading": "Formularies",
                        "siblings_text": None,
                        "resource_value": "https://www.example.com/formularies/ga-2022-06-tykerb.pdf",
                        "base_url": "https://www.example.com/formularies/",
                        "playbook_context": None,
                    },
                )
            ],
        )
    )

    docs.append(
        RetrievedDocument(
            site_id=site_id_a,
            name="Trastuzumab (224905) June 2022",
            checksum="0000000000000000000000000000001A",
            effective_date=datetime(2022, 6, 1, tzinfo=timezone.utc),
            document_type="Formulary",
            doc_type_confidence=1,
            therapy_tags=[
                TherapyTag(text="trastuzumab", name="Trastuzumab", code="224905", focus=1)
            ],
            indication_tags=[IndicationTag(text="TDAP", code=155, focus=False)],
            file_size=1400000,
            locations=[
                RetrievedDocumentLocation(
                    site_id=site_id_a,
                    url="https://www.example.com/formularies/ga-2022-06-trastuzumab.pdf",
                    link_text="trastuzumab",
                    closest_heading="Formularies",
                    base_url="https://www.example.com/formularies/",
                    context_metadata={
                        "link_text": "trastuzumab",
                        "element_id": None,
                        "closest_heading": "Formularies",
                        "siblings_text": None,
                        "resource_value": "https://www.example.com/formularies/ga-2022-06-trastuzumab.pdf",
                        "base_url": "https://www.example.com/formularies/",
                        "playbook_context": None,
                    },
                )
            ],
        )
    )

    for doc in docs:
        doc = await doc.save()
        rt_doc_location = doc.locations[0]

        doc_document = DocDocument(
            retrieved_document_id=doc.id,  # type: ignore
            name=doc.name,
            checksum=doc.checksum,
            text_checksum=doc.text_checksum,
            document_type=doc.document_type,
            doc_type_confidence=doc.doc_type_confidence,
            end_date=doc.end_date,
            effective_date=doc.effective_date,
            last_updated_date=doc.last_updated_date,
            last_reviewed_date=doc.last_reviewed_date,
            next_review_date=doc.next_review_date,
            next_update_date=doc.next_update_date,
            published_date=doc.published_date,
            lang_code=doc.lang_code,
            therapy_tags=doc.therapy_tags,
            indication_tags=doc.indication_tags,
            file_extension=doc.file_extension,
            identified_dates=doc.identified_dates,
            last_collected_date=doc.last_collected_date,
            first_collected_date=doc.first_collected_date,
            locations=[DocDocumentLocation(**rt_doc_location.dict())],
        )

        doc_document.set_final_effective_date()

        await doc_document.save()


@pytest.mark.asyncio()
async def test_this(mock_s3_client):  # noqa
    random_name = str(random())
    await init_db(mock=True, database_name=random_name)
    await load_retrieved_docs()

    lineage_service = LineageService(logger=logging)  # noqa
