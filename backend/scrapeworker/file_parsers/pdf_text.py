import os

import pytest

from backend.scrapeworker.file_parsers import pdf

current_path = os.path.dirname(os.path.realpath(__file__))
fixture_path = os.path.join(current_path, "__fixtures__")


@pytest.mark.asyncio
async def test_docx():
    file_path = os.path.join(fixture_path, "test_tm.pdf")

    parser = pdf.PdfParse(file_path, url=file_path)
    await parser.parse()
    # ™ symbol does not exist in Latin1 encoding, test confirms extraction with utf-8 is successful
    assert "®" in parser.result["text"]
    assert "™" in parser.result["text"]
    assert "®" in parser.result["metadata"]["Keywords"]
    assert "™" in parser.result["metadata"]["Keywords"]
