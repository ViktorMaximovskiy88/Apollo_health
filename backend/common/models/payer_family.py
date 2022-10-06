from beanie import PydanticObjectId
from pydantic import BaseModel

from backend.common.models.base_document import BaseDocument


class NewPayerFamily(BaseModel):
    name: str
    document_type: str
    description: str | None = None
    site_id: PydanticObjectId


class UpdatePayerFamily(BaseModel):
    name: str | None = None
    document_type: str | None = None
    description: str | None = None
    site_id: PydanticObjectId | None = None


class PayerFamily(BaseDocument, NewPayerFamily):
    disabled: bool = False
