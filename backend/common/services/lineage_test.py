import logging
from datetime import datetime, timezone

import pytest
from beanie import PydanticObjectId

from backend.common.db.init import init_db
from backend.common.models.document import RetrievedDocument
from backend.common.models.shared import IndicationTag, RetrievedDocumentLocation, TherapyTag
from backend.common.services.lineage import LineageService

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
            indication_tags=[IndicationTag(text="TDAP", indication_number=155, focus=False)],
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
            indication_tags=[IndicationTag(text="TDAP", indication_number=155, focus=False)],
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
            indication_tags=[IndicationTag(text="TDAP", indication_number=155, focus=False)],
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

    [await doc.save() for doc in docs]


@pytest.mark.asyncio()
async def test_this():
    await init_db()
    await load_retrieved_docs()

    lineage_service = LineageService(logger=logging)
    await lineage_service.process_lineage_for_site(site_id_a)
