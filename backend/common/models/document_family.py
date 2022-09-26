from beanie import PydanticObjectId
from pydantic import BaseModel

from backend.common.models.base_document import BaseDocument


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
    site_id: PydanticObjectId
    payer_info: PayerInfo = PayerInfo()
    relevance: list[str] = []
    legacy_relevance: list[str] = []
    field_groups: list[str] = []


class UpdateDocumentFamily(BaseModel):
    name: str | None = None
    document_type: str | None = None
    description: str | None = None
    site_id: PydanticObjectId | None = None
    payer_info: PayerInfo | None = None
    relevance: list[str] = []
    disabled: bool | None = None


class DocumentFamily(BaseDocument, NewDocumentFamily):
    disabled: bool
