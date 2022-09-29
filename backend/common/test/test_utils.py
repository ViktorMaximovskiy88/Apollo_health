import tempfile
from contextlib import contextmanager

import pytest

from backend.common.storage.client import BaseS3Client


@pytest.fixture
def mock_s3_client(monkeypatch: pytest.MonkeyPatch):
    def write_object(self, relative_key: str, temp_object_path: str, content_type: str) -> None:
        assert type(relative_key) == str
        assert type(temp_object_path) == str
        assert type(content_type) == str
        return None

    def write_object_mem(self, relative_key: str, object: bytes) -> None:
        assert type(relative_key) == str
        assert type(object) == bytes
        return None

    @contextmanager
    def read_object_to_tempfile(self, relative_key: str):
        with tempfile.NamedTemporaryFile() as temp:
            f = open(relative_key, "rb")
            temp.write(f.read())
            yield temp.name

    def object_exists(self, relative_key: str) -> bool:
        assert type(relative_key) == str
        return False

    monkeypatch.delattr(BaseS3Client, "__init__")
    monkeypatch.setattr(BaseS3Client, "write_object_mem", write_object_mem)
    monkeypatch.setattr(BaseS3Client, "write_object", write_object)
    monkeypatch.setattr(BaseS3Client, "read_object_to_tempfile", read_object_to_tempfile)
    monkeypatch.setattr(BaseS3Client, "object_exists", object_exists)
