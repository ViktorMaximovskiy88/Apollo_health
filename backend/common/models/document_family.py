from beanie import PydanticObjectId
from pydantic import BaseModel

from backend.common.models.base_document import BaseDocument


class NewDocumentFamily(BaseModel):
    name: str
    document_type: str
    description: str | None = None
    site_id: PydanticObjectId
    relevance: list[str] = []


class UpdateDocumentFamily(BaseModel):
    name: str | None = None
    document_type: str | None = None
    description: str | None = None
    site_id: PydanticObjectId | None = None
    relevance: list[str] = []
    disabled: bool | None = None


class DocumentFamily(BaseDocument, NewDocumentFamily):
    disabled: bool
