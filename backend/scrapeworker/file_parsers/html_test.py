import os

import aiofiles
import pytest

from backend.scrapeworker.file_parsers import html

current_path = os.path.dirname(os.path.realpath(__file__))
fixture_path = os.path.join(current_path, "__fixtures__")


@pytest.mark.asyncio
async def test_html():
    file_path = os.path.join(fixture_path, "test.html")
    expected_path = os.path.join(fixture_path, "test_html.txt")

    async with aiofiles.open(expected_path, mode="r") as file:
        expected_text = await file.read()

    parser = html.HtmlParser(file_path, url=file_path)
    await parser.parse()

    assert parser.text == expected_text
    assert parser.metadata == {}
