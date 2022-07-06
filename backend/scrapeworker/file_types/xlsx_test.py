import os
import pytest
import aiofiles
from backend.scrapeworker.file_types.xlsx import xlsx_text, xlsx_info

current_path = os.path.dirname(os.path.realpath(__file__))
fixture_path = os.path.join(current_path, "__fixtures__")


@pytest.mark.asyncio
async def test_xlsx_text():
    file_path = os.path.join(fixture_path, "test.xlsx")
    expected_path = os.path.join(fixture_path, "test_xlsx.txt")

    async with aiofiles.open(expected_path, mode="r") as file:
        expected_text = await file.read()

    text = xlsx_text(file_path)
    assert text == expected_text


@pytest.mark.asyncio
async def test_xlsx_info():
    file_path = os.path.join(fixture_path, "test.xlsx")

    metadata = xlsx_info(file_path)
    assert metadata["title"] == "Test Title xlsx"
    assert metadata["subject"] == "Test Subject xlsx"
    assert metadata["category"] == "Test Category xlsx"
