import os
import pytest
import aiofiles
from backend.scrapeworker.file_parsers import docx

current_path = os.path.dirname(os.path.realpath(__file__))
fixture_path = os.path.join(current_path, "__fixtures__")


@pytest.mark.asyncio
async def test_docx():
    file_path = os.path.join(fixture_path, "test.docx")
    expected_path = os.path.join(fixture_path, "test_docx.txt")

    async with aiofiles.open(expected_path, mode="r") as file:
        expected_text = await file.read()

    parser = docx.DocxParser(file_path, url=file_path)
    await parser.parse()
    assert parser.text == expected_text
    assert parser.metadata["title"] == "Test Title docx"
    assert parser.metadata["subject"] == "Test Subject docx"
    assert parser.metadata["category"] == "Test Category docx"
