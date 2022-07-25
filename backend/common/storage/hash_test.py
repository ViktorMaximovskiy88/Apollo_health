import os
import pytest
import aiofiles
from asyncio import gather
from backend.scrapeworker.file_parsers import docx
from backend.common.storage.hash import hash_full_text, hash_bytes

current_path = os.path.dirname(os.path.realpath(__file__))
fixture_path = os.path.join(current_path, "__fixtures__")


async def _read_fixture_file(file_name: str):
    file_path = os.path.join(fixture_path, file_name)
    async with aiofiles.open(file_path, mode="r", encoding="ISO-8859-1") as f:
        content = await f.read()
    return content.encode("utf-8")


async def _parse_fixture_file(file_name: str):
    file_path = os.path.join(fixture_path, file_name)
    parser = docx.DocxParser(file_path, url=file_path)
    parsed = await parser.parse()
    return parsed["text"]


@pytest.mark.asyncio
async def test_hash_full_text_same_text():

    content_a, content_b, content_c = await gather(
        _parse_fixture_file("example-desktop-word.docx"),
        _parse_fixture_file("example-google-docs.docx"),
        _parse_fixture_file("example-office365-word.docx"),
    )

    # all parsed texts are the same
    assert content_a == content_b == content_c

    file_a, file_b, file_c = await gather(
        _read_fixture_file("example-desktop-word.docx"),
        _read_fixture_file("example-google-docs.docx"),
        _read_fixture_file("example-office365-word.docx"),
    )

    file_hash_a = hash_bytes(file_a)
    file_hash_b = hash_bytes(file_b)
    file_hash_c = hash_bytes(file_c)

    assert file_hash_a == "5cc1f4c6abcb9d91786f5e06cad3b75b"
    assert file_hash_b == "529e116754359061a6de6ef788411978"
    assert file_hash_c == "64fc0dd1f54be178c2fa2c528232ec72"

    # none of the files are the same, in fact they range in size from 6kb to 12kb
    assert file_hash_a != file_hash_b != file_hash_c

    content_hash_a = hash_full_text(content_a)
    content_hash_b = hash_full_text(content_b)
    content_hash_c = hash_full_text(content_c)

    # the real purpose, all content hashes match
    assert content_hash_a == content_hash_b == content_hash_c
