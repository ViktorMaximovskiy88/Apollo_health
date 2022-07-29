from beanie import PydanticObjectId
from pydantic import BaseModel

from backend.common.models.base_document import BaseDocument


class NewDocumentFamily(BaseModel):
    name: str
    document_type: str | None = None
    description: str | None = None
    sites: list[PydanticObjectId] = []
    um_package: str | None = None
    benefit_type: str | None = None
    document_type_threshold: str | None = None
    therapy_tag_status_threshold: int | None = None
    lineage_threshold: int | None = None
    relevance: list[str] = []


class UpdateDocumentFamily(BaseModel):
    name: str | None = None
    document_type: str | None = None
    description: str | None = None
    sites: list[PydanticObjectId] = []
    um_package: str | None = None
    benefit_type: str | None = None
    document_type_threshold: str | None = None
    therapy_tag_status_threshold: int | None = None
    lineage_threshold: int | None = None
    relevance: list[str] = []
    disabled: bool | None = None


class DocumentFamily(BaseDocument, NewDocumentFamily):
    disabled: bool
