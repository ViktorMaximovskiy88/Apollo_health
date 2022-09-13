from backend.common.core.enums import SearchableType
from backend.common.models.base_document import BaseDocument


class SearchCodeSet(BaseDocument):
    type: SearchableType
    codes: set[str]
