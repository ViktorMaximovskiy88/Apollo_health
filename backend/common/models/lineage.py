from datetime import datetime
from pydantic import BaseModel
from beanie import PydanticObjectId
from backend.common.models.base_document import BaseDocument


class LineageAttrs(BaseModel):
    state_name: str | None
    state_abbr: str | None
    year_part: int | None
    month_part: int | None
    month_name: str | None


class Lineage(BaseDocument):
    entries: list[PydanticObjectId] = []


class LineageCompare(BaseDocument):
    doc_id: PydanticObjectId
    site_id: PydanticObjectId
    lineage_id: PydanticObjectId | None
    element_text: str | None
    filename: str | None

    # doc info
    document_type: str | None
    effective_date: datetime | None
    focus_therapy_tags: list[int] = []
    ref_therapy_tags: list[int] = []
    focus_indication_tags: list[int] = []
    ref_indication_tags: list[int] = []

    # tokens
    filename_tokens: list[str] = []
    pathname_tokens: list[str] = []
    element_text_tokens: list[str] = []
    parent_text_tokens: list[str] = []
    sibling_text_tokens: list[str] = []

    filename: LineageAttrs | None
    pathname: LineageAttrs | None
    element: LineageAttrs | None
    parent: LineageAttrs | None
    siblings: LineageAttrs | None
