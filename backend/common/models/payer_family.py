from beanie import Indexed, PydanticObjectId

from backend.common.models.base_document import BaseDocument, BaseModel


class PayerFamily(BaseDocument):
    name: Indexed(str)  # type: ignore
    site_ids: list[PydanticObjectId] = []
    payer_type: str | None = None
    payer_ids: list[str] = []
    channels: list[str] = []
    benefits: list[str] = []
    plan_types: list[str] = []
    regions: list[str] = []
    disabled: bool = False
    doc_doc_count: int = 0


class NewPayerFamily(BaseModel):
    name: str
    site_ids: list[PydanticObjectId] = []
    payer_type: str | None = None
    payer_ids: list[str] = []
    channels: list[str] = []
    benefits: list[str] = []
    plan_types: list[str] = []
    regions: list[str] = []
    doc_doc_count: int = 0


class UpdatePayerFamily(BaseModel):
    name: str | None = None
    site_ids: list[PydanticObjectId] = []
    payer_type: str | None = None
    payer_ids: list[str] | None = None
    channels: list[str] | None = None
    benefits: list[str] | None = None
    plan_types: list[str] | None = None
    regions: list[str] | None = None
    disabled: bool | None = None
