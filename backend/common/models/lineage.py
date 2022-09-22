from datetime import datetime

from beanie import PydanticObjectId
from pydantic import BaseModel

from backend.common.core.enums import LangCode
from backend.common.models.base_document import BaseDocument


class DocumentAttrs(BaseModel):
    state_name: str | None
    state_abbr: str | None
    year_part: int | None
    month_part: int | None
    month_name: str | None
    month_abbr: str | None
    lang_code: LangCode | None  # we dont want other or unknown except for doc case


class DocumentAnalysis(BaseDocument):
    retrieved_document_id: PydanticObjectId
    site_id: PydanticObjectId
    lineage_id: PydanticObjectId | None
    is_current_version: bool = False

    state_abbr: str | None
    state_name: str | None
    year_part: int | None
    month_name: str | None
    month_abbr: str | None
    lang_code: LangCode | None  # we dont want other or unknown except for doc case

    # location info
    element_text: str | None
    parent_text: str | None
    siblings_text: str | None
    filename_text: str | None
    pathname_text: str | None

    # doc info
    document_type: str | None
    effective_date: datetime | None
    file_size: int | None

    focus_therapy_tags: list[int] = []
    ref_therapy_tags: list[int] = []
    focus_indication_tags: list[int] = []
    ref_indication_tags: list[int] = []

    # tokens
    filename_tokens: list[str] = []
    pathname_tokens: list[str] = []

    # explicit matches per thing (repetition increase assuredness)
    filename: DocumentAttrs | None
    pathname: DocumentAttrs | None
    element: DocumentAttrs | None
    parent: DocumentAttrs | None
    siblings: DocumentAttrs | None

    doc_type_vectors: list[list[float]] = []
