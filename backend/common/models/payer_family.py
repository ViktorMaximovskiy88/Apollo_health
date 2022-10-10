from beanie import PydanticObjectId
from pydantic import BaseModel

from backend.common.models.base_document import BaseDocument


class PayerFamily(BaseDocument):
    name: str
    document_type: str
    site_id: PydanticObjectId = "siteID"
    payer_type: str = "plan"
    payer_ids: list[str] = []
    channels: list[str] = []
    benefits: list[str] = []
    plan_types: list[str] = []
    regions: list[str] = []
    disabled: bool = False


class NewPayerFamily(BaseModel):
    name: str
    document_type: str
    site_id: PydanticObjectId
    payer_type: str = "plan"
    payer_ids: list[str] = []
    channels: list[str] = []
    benefits: list[str] = []
    plan_types: list[str] = []
    regions: list[str] = []


class UpdatePayerFamily(BaseModel):
    name: str | None = None
    document_type: str | None = None
    site_id: PydanticObjectId | None = None
    payer_type: str | None = None
    payer_ids: list[str] | None = None
    channels: list[str] | None = None
    benefits: list[str] | None = None
    plan_types: list[str] | None = None
    regions: list[str] | None = None
    disabled: bool | None = None
