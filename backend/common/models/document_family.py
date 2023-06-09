from beanie import PydanticObjectId

from backend.common.models.base_document import BaseDocument, BaseModel


class PayerInfo(BaseModel):
    payer_type: str = "plan"
    payer_ids: list[str] = []
    channels: list[str] = []
    benefits: list[str] = []
    plan_types: list[str] = []
    regions: list[str] = []


class NewDocumentFamily(BaseModel):
    name: str
    document_type: str
    description: str | None = None
    site_ids: list[PydanticObjectId] = []
    relevance: list[str] = []
    legacy_relevance: list[str] = []
    field_groups: list[str] = []
    doc_doc_count: int = 0


class UpdateDocumentFamily(BaseModel):
    name: str | None = None
    document_type: str | None = None
    description: str | None = None
    site_ids: list[PydanticObjectId] = []
    relevance: list[str] = []
    disabled: bool | None = None
    field_groups: list[str] = []
    legacy_relevance: list[str] = []


class DocumentFamily(BaseDocument, NewDocumentFamily):
    disabled: bool = False
