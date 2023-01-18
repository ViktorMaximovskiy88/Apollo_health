from typing import Any

from beanie import Indexed

from backend.common.models.base_document import BaseDocument


class AppConfig(BaseDocument):
    key: Indexed(str)
    data: dict[str, Any]

    @classmethod
    async def get_tricare_tokens(cls):
        return await cls.find({"key": "tricare_tokens"}).to_list()
