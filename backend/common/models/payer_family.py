from beanie import Indexed, PydanticObjectId

from backend.common.models.base_document import BaseDocument, BaseModel


class PayerFamily(BaseDocument):
    name: Indexed(str, unique=True)  # type: ignore
    site_id: PydanticObjectId | None = None
    payer_type: str | None = None
    payer_ids: list[str] = []
    channels: list[str] = []
    benefits: list[str] = []
    plan_types: list[str] = []
    regions: list[str] = []
    disabled: bool = False
    auto_generated: bool = True


class NewPayerFamily(BaseModel):
    name: str
    site_id: PydanticObjectId | None = None
    payer_type: str | None = None
    payer_ids: list[str] = []
    channels: list[str] = []
    benefits: list[str] = []
    plan_types: list[str] = []
    regions: list[str] = []
    auto_generated: bool = True


class UpdatePayerFamily(BaseModel):
    name: str | None = None
    site_id: PydanticObjectId | None = None
    payer_type: str | None = None
    payer_ids: list[str] | None = None
    channels: list[str] | None = None
    benefits: list[str] | None = None
    plan_types: list[str] | None = None
    regions: list[str] | None = None
    disabled: bool | None = None
    auto_generated: bool | None = None
