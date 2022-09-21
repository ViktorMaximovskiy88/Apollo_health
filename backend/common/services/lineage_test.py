import logging
from datetime import datetime, timezone

import pytest
from beanie import PydanticObjectId

from backend.common.db.init import init_db
from backend.common.models.document import RetrievedDocument
from backend.common.models.lineage import DocumentAnalysis
from backend.common.models.shared import (
    IndicationTag,
    RetrievedDocumentLocation,
    SiteLocation,
    TherapyTag,
)
from backend.common.services.lineage import LineageService


async def load_retrieved_docs() -> list[RetrievedDocument]:
    docs: list[RetrievedDocument] = []
    site_id_a = PydanticObjectId("00000000000000000000000a")
    site_id_b = PydanticObjectId("00000000000000000000000b")
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

    for doc in docs:
        await doc.save()

    print(docs)
    # no focus match

    # partial focus match


@pytest.mark.asyncio()
async def test_this():
    await init_db()
    lineage_service = LineageService(log=logging)
    await lineage_service.process_lineage_for_sites()
    await load_retrieved_docs()
