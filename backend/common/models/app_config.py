from typing import Any

from beanie import Indexed

from backend.common.models.base_document import BaseDocument


class AppConfig(BaseDocument):
    key: Indexed(str)
    data: dict[str, Any] | list[Any]

    @classmethod
    async def get_tricare_tokens(cls) -> list[str]:
        result = await cls.find_one({"key": "tricare_tokens"})
        return result.data
