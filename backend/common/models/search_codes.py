from backend.common.core.enums import SearchableType
from backend.common.models.base_document import BaseDocument


class SearchCodeSet(BaseDocument):
    type: SearchableType
    codes: set[str]

    @classmethod
    async def get_tricare_tokens(cls) -> list[str]:
        result = await cls.find_one({"type": SearchableType.TRICARE})
        return result.codes

    @classmethod
    async def get_universal_tokens(cls) -> list[str]:
        result = await cls.find_one({"type": SearchableType.UNIVERSAL})
        return result.codes
