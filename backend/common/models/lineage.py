from datetime import datetime

from beanie import PydanticObjectId
from pydantic import Field

from backend.common.models.base_document import BaseModel


class LineageDoc(BaseModel):
    id: PydanticObjectId = Field(None, alias="_id")
    name: str | None
    document_type: str | None
    final_effective_date: datetime | None
    previous_doc_doc_id: PydanticObjectId | None
    retrieved_document_id: PydanticObjectId | None
    is_current_version: bool | None
    lineage_id: PydanticObjectId | None
    file_extension: str | None
    checksum: str | None
    classification_status: str | None
    first_collected_date: datetime | None
    last_collected_date: datetime | None
    priority: int | None
