from datetime import datetime
from enum import Enum

from beanie import Indexed, PydanticObjectId

from backend.common.models.base_document import BaseDocument, BaseModel


class HoldType(str, Enum):
    ClassificationHold = "Classification Hold"
    DocPayerHold = "Document and Payer Family Hold"
    TranslationConfigHold = "Translation Config Hold"


class Comment(BaseDocument):
    time: datetime
    target_id: Indexed(PydanticObjectId)  # type: ignore
    user_id: PydanticObjectId
    text: str
    type: HoldType | None = None


class UpdateComment(BaseModel):
    text: str


class NewComment(BaseModel):
    text: str
    target_id: PydanticObjectId
    type: HoldType | None = None
