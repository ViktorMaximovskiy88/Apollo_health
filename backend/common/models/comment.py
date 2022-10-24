from datetime import datetime

from beanie import Indexed, PydanticObjectId

from backend.common.models.base_document import BaseDocument, BaseModel


class Comment(BaseDocument):
    time: datetime
    target_id: Indexed(PydanticObjectId)  # type: ignore
    user_id: PydanticObjectId
    text: str


class UpdateComment(BaseModel):
    text: str


class NewComment(BaseModel):
    text: str
    target_id: PydanticObjectId
