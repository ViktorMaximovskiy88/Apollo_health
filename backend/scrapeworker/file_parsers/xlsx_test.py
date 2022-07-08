import os
import pytest
import aiofiles
from backend.scrapeworker.file_parsers import xlsx

current_path = os.path.dirname(os.path.realpath(__file__))
fixture_path = os.path.join(current_path, "__fixtures__")


@pytest.mark.asyncio
async def test_xlsx():
    file_path = os.path.join(fixture_path, "test.xlsx")
    expected_path = os.path.join(fixture_path, "test_xlsx.txt")

    async with aiofiles.open(expected_path, mode="r") as file:
        expected_text = await file.read()

    parser = xlsx.XlsxParser(file_path, url=file_path)
    await parser.parse()

    assert parser.text == expected_text
    assert parser.metadata["title"] == "Test Title xlsx"
    assert parser.metadata["subject"] == "Test Subject xlsx"
    assert parser.metadata["category"] == "Test Category xlsx"
