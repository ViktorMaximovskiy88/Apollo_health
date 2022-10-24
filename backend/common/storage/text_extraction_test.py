import os
import tempfile

import aiofiles
import aiofiles.os
import pytest

from backend.common.storage.hash import get_document_hash
from backend.common.storage.text_extraction import TextExtractor

current_path = os.path.dirname(os.path.realpath(__file__))
fixture_path = os.path.join(current_path, "__fixtures__")


@pytest.mark.asyncio
async def test_html_hash():
    file_path = os.path.join(fixture_path, "html_fixture.html")
    async with aiofiles.open(file_path, "rb") as file:
        doc = await file.read()
    extractor = TextExtractor(document_bytes=doc)
    await extractor.extract()
    hash = get_document_hash(extractor)
    assert hash == "43764587756d5ffe002ec4080fea80fe"


@pytest.mark.asyncio
async def test_pdf_hash():
    file_path = os.path.join(fixture_path, "pdf_fixture.pdf")
    with tempfile.NamedTemporaryFile() as temp:
        async with aiofiles.open(temp.name, "wb") as fd:
            async with aiofiles.open(file_path, "rb") as file:
                doc = await file.read()
                await fd.write(doc)
            await aiofiles.os.stat(str(temp.name))
            extractor = TextExtractor(
                document_bytes=doc, mimetype="application/pdf", temp_path=temp.name
            )
            await extractor.extract()
            hash = get_document_hash(extractor)
            assert hash == "e24d0bdc1e308abc1abb60889be537ad"
