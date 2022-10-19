from datetime import datetime, timezone

from beanie import Insert, PydanticObjectId, Replace, before_event
from pydantic import Field

from backend.common.core.enums import LangCode
from backend.common.models.base_document import BaseDocument, BaseModel


class LineageDoc(BaseModel):
    id: PydanticObjectId = Field(None, alias="_id")
    name: str | None
    document_type: str | None
    final_effective_date: datetime | None
    previous_doc_id: PydanticObjectId | None
    is_current_version: bool | None
    lineage_id: PydanticObjectId | None
    file_extension: str | None
    checksum: str | None


class DocumentAttrs(BaseModel):
    state_name: str | None = None
    state_abbr: str | None = None
    year_part: int | None = None
    month_part: int | None = None
    month_name: str | None = None
    month_abbr: str | None = None
    lang_code: LangCode | None = None  # we dont want other or unknown except for doc case


class DocumentAnalysis(BaseDocument):
    retrieved_document_id: PydanticObjectId
    site_id: PydanticObjectId
    lineage_id: PydanticObjectId | None = None
    is_current_version: bool = False

    name: str | None = None
    state_abbr: str | None = None
    state_name: str | None = None
    year_part: int | None = None
    month_name: str | None = None
    month_abbr: str | None = None
    lang_code: LangCode | None = None  # we dont want other or unknown except for doc case = None

    # location info
    element_text: str | None = None
    parent_text: str | None = None
    siblings_text: str | None = None
    filename_text: str | None = None
    pathname_text: str | None = None

    # doc info
    document_type: str | None = None
    final_effective_date: datetime | None = None
    file_size: int | None = None

    focus_therapy_tags: list[int] = []
    ref_therapy_tags: list[int] = []
    focus_indication_tags: list[int] = []
    ref_indication_tags: list[int] = []

    # tokens
    filename_tokens: list[str] = []
    pathname_tokens: list[str] = []

    # explicit matches per thing (repetition increase assuredness)
    filename: DocumentAttrs | None = None
    pathname: DocumentAttrs | None = None
    element: DocumentAttrs | None = None
    parent: DocumentAttrs | None = None
    siblings: DocumentAttrs | None = None

    doc_vectors: list[list[float]] = []

    created_at: datetime | None = None
    updated_at: datetime | None = None

    @before_event(Insert)
    def insert_dates(self):
        now = datetime.now(tz=timezone.utc)
        self.created_at = now
        self.updated_at = now

    @before_event(Replace)
    def replace_dates(self):
        self.updated_at = datetime.now(tz=timezone.utc)
