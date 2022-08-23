import os

import pytest

from backend.common.storage.client import BaseS3Client
from backend.common.storage.text_handler import TextHandler
from backend.common.test.test_utils import mock_s3_client  # noqa

current_path = os.path.dirname(os.path.realpath(__file__))
fixture_path = os.path.join(current_path, "__fixtures__")


@pytest.mark.asyncio
async def test_create_diff(mock_s3_client):  # noqa
    handler = TextHandler()
    a_name = os.path.join(fixture_path, "diff_test_a")
    b_name = os.path.join(fixture_path, "diff_test_b")
    diff_name, _ = await handler.create_diff(a_name, b_name)

    assert diff_name == f"{a_name}-{b_name}"


@pytest.mark.asyncio
async def test_create_no_diff(mock_s3_client, monkeypatch: pytest.MonkeyPatch):  # noqa
    def object_exists(self, relative_key) -> bool:
        assert type(relative_key) == str
        return True

    def read_object(self, relative_key) -> bytes:
        assert type(relative_key) == str
        return bytes("content as bytes", "utf-8")

    monkeypatch.setattr(BaseS3Client, "object_exists", object_exists)
    monkeypatch.setattr(BaseS3Client, "read_object", read_object)
    handler = TextHandler()
    a_name = os.path.join(fixture_path, "diff_test_a")
    b_name = os.path.join(fixture_path, "diff_test_b")
    diff_name, diff_out = await handler.create_diff(a_name, b_name)

    assert diff_name == f"{a_name}-{b_name}"
    assert diff_out == bytes("content as bytes", "utf-8")


@pytest.mark.asyncio
async def test_save_text(mock_s3_client):  # noqa
    handler = TextHandler()
    a_name = os.path.join(fixture_path, "diff_test_a.txt")
    content = open(a_name, "r").read()
    text_checksum = await handler.save_text(content)
    assert text_checksum == "43bbf105d938ef980fd1625cefa210cf"
