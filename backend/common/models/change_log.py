from datetime import datetime
from typing import Any
from beanie import Indexed, PydanticObjectId
from backend.common.models.base_document import BaseDocument


class ChangeLog(BaseDocument):
    user_id: PydanticObjectId | None
    target_id: Indexed(PydanticObjectId)  # type: ignore
    collection: str
    time: datetime
    action: str
    delta: Any
