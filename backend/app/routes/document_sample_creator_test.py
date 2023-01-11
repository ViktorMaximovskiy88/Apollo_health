from pathlib import Path

import fitz
import pytest

from backend.app.routes.document_sample_creator import DocumentSampleCreator


@pytest.mark.asyncio
async def test_take_document_sample():
    input_file = Path(__file__).parent.joinpath("mocks", "pdf_fixture.pdf")

    with fitz.open(input_file) as input_doc:
        for page in input_doc.pages(start=0, stop=1):
            first_page_text = page.get_text()

        sampler = DocumentSampleCreator()
        sample_bytes = sampler.sample_file(stream=input_doc.write())

        all_sample_text = ""
        with fitz.open(stream=sample_bytes) as pdf:  # type: ignore
            for page in pdf.pages():
                all_sample_text += page.get_text()

        assert all_sample_text == first_page_text
