from io import BufferedReader
from pathlib import Path

import pdfplumber
import pytest

from backend.app.routes.document_sample_creator import DocumentSampleCreator


@pytest.mark.asyncio
async def test_take_document_sample():
    input = Path(__file__).parent.joinpath("mocks", "pdf_fixture.pdf")
    with open(input, "rb") as infile:
        with pdfplumber.open(infile) as pdf:
            first_page_text = pdf.pages[0].extract_text()

        sampler = DocumentSampleCreator()
        sample = sampler.sample_file(infile)
        sample.seek(0)

        all_sample_text = ""
        with pdfplumber.open(BufferedReader(sample)) as pdf:  # type: ignore
            for page in pdf.pages:
                all_sample_text += page.extract_text()
        assert all_sample_text == first_page_text
