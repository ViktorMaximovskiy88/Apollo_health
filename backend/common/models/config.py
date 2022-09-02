from typing import Any

from backend.common.models.base_document import BaseDocument


class Config(BaseDocument):
    key: str
    data: dict[str, Any]
