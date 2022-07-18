import pytest
import os

from backend.common.test.test_utils import mock_s3_client
from backend.common.storage.client import BaseS3Client
from backend.scrapeworker.common.text_handler import TextHandler

current_path = os.path.dirname(os.path.realpath(__file__))
fixture_path = os.path.join(current_path, "__fixtures__")


@pytest.mark.asyncio
async def test_create_diff(mock_s3_client):
    handler = TextHandler()
    a_name = os.path.join(fixture_path, "diff_test_a")
    b_name = os.path.join(fixture_path, "diff_test_b")
    diff_checksum = await handler.create_diff(a_name, b_name)

    assert diff_checksum == f"{a_name}-{b_name}"


@pytest.mark.asyncio
async def test_create_no_diff(mock_s3_client, monkeypatch: pytest.MonkeyPatch):
    def object_exists(self, relative_key) -> bool:
        assert type(relative_key) == str
        return True

    monkeypatch.setattr(BaseS3Client, "object_exists", object_exists)
    handler = TextHandler()
    a_name = os.path.join(fixture_path, "diff_test_a")
    b_name = os.path.join(fixture_path, "diff_test_b")
    diff_checksum = await handler.create_diff(a_name, b_name)

    assert diff_checksum == None


@pytest.mark.asyncio
async def test_save_text(mock_s3_client):
    handler = TextHandler()
    a_name = os.path.join(fixture_path, "diff_test_a")
    text_checksum = await handler.save_text(a_name)

    assert text_checksum == "4704c18b0c4d9e643db3e9ea61442ab8"
