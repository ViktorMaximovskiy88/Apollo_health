from datetime import datetime

from beanie import PydanticObjectId
from pydantic import BaseModel

from backend.common.models.base_document import BaseDocument


class LineageAttrs(BaseModel):
    state_name: str | None
    state_abbr: str | None
    year_part: int | None
    month_part: int | None
    month_name: str | None
    month_abbr: str | None


class Lineage(BaseDocument):
    entries: list[PydanticObjectId] = []


class LineageCompare(BaseDocument):
    doc_id: PydanticObjectId
    site_id: PydanticObjectId
    lineage_id: PydanticObjectId | None

    state_abbr: str | None
    state_name: str | None
    year_part: int | None
    month_name: str | None
    month_abbr: str | None

    # location info
    element_text: str | None
    parent_text: str | None
    siblings_text: str | None
    filename_text: str | None
    pathname_text: str | None

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

    # explicit matches per thing (repetiion increase assuredness)
    filename: LineageAttrs | None
    pathname: LineageAttrs | None
    element: LineageAttrs | None
    parent: LineageAttrs | None
    siblings: LineageAttrs | None
