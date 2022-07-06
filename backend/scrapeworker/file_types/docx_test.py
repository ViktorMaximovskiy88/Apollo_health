import os
import pytest
import aiofiles
from backend.scrapeworker.file_types.docx import docx_text, docx_info

current_path = os.path.dirname(os.path.realpath(__file__))
fixture_path = os.path.join(current_path, "__fixtures__")


@pytest.mark.asyncio
async def test_docx_text():
    file_path = os.path.join(fixture_path, "test.docx")
    expected_path = os.path.join(fixture_path, "test_docx.txt")

    async with aiofiles.open(expected_path, mode="r") as file:
        expected_text = await file.read()

    text = docx_text(file_path)
    assert text == expected_text


@pytest.mark.asyncio
async def test_docx_docx_info():
    file_path = os.path.join(fixture_path, "test.docx")

    metadata = docx_info(file_path)
    assert metadata["title"] == "Test Title docx"
    assert metadata["subject"] == "Test Subject docx"
    assert metadata["category"] == "Test Category docx"
