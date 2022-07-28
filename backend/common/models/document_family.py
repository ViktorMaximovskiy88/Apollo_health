from beanie import PydanticObjectId
from pydantic import BaseModel

from backend.common.models.base_document import BaseDocument


class DocumentFamily(BaseDocument):
    name: str
    document_type: str | None = None
    description: str | None = None
    sites: list[PydanticObjectId] = []
    um_package: str | None = None
    benefit_type: str | None = None
    document_type_threshold: str | None = None
    therapy_tag_status_threshold: int | None = None
    therapy_tag_states_threshold: int | None = None
    lineage_threshold: int | None = None
    relevance: list[str] = []


class UpdateSite(BaseModel):
    name: str | None = None
    document_type: str | None = None
    description: str | None = None
    sites: list[PydanticObjectId] = []
    um_package: str | None = None
    benefit_type: str | None = None
    document_type_threshold: str | None = None
    therapy_tag_status_threshold: int | None = None
    therapy_tag_states_threshold: int | None = None
    lineage_threshold: int | None = None
    relevance: list[str] = []
