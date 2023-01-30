from datetime import datetime, timezone

from beanie import Indexed, Insert, PydanticObjectId, Replace, before_event
from pydantic import Field

from backend.common.core.enums import ApprovalStatus, LangCode
from backend.common.models.base_document import BaseDocument, BaseModel


class DocumentAnalysisHeader(BaseModel):
    id: PydanticObjectId = Field(None, alias="_id")
    doc_document_id: PydanticObjectId
    site_id: PydanticObjectId


class DocumentAttrs(BaseModel):
    state_name: str | None = None
    state_abbr: str | None = None
    year_part: int | None = None
    month_part: int | None = None
    month_name: str | None = None
    month_abbr: str | None = None
    lang_code: LangCode | None = None  # we dont want other or unknown except for doc case


# TODO hate the name but w/e
class DocumentAnalysisLineage(BaseModel):
    doc_document_id: PydanticObjectId
    retrieved_document_id: PydanticObjectId
    site_id: PydanticObjectId
    classification_status: ApprovalStatus | None = None
    lineage_id: PydanticObjectId | None = None
    previous_doc_doc_id: PydanticObjectId | None = None
    is_current_version: bool | None = None


class DocumentAnalysis(BaseDocument):
    retrieved_document_id: Indexed(PydanticObjectId)  # type: ignore
    doc_document_id: Indexed(PydanticObjectId) | None = None  # type: ignore
    site_id: Indexed(PydanticObjectId)  # type: ignore
    lineage_id: Indexed(PydanticObjectId) | None = None
    confidence: float = 0.0
    is_current_version: bool = False
    previous_doc_doc_id: PydanticObjectId | None = None

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
    doc_vectors: list[list[float]] = []
    token_count: int = 0

    # tags
    focus_therapy_tags: list[str | int] = []
    ref_therapy_tags: list[str | int] = []
    focus_indication_tags: list[int] = []
    ref_indication_tags: list[int] = []

    url_focus_therapy_tags: list[str | int] = []
    url_focus_indication_tags: list[int] = []

    link_focus_therapy_tags: list[str | int] = []
    link_focus_indication_tags: list[int] = []

    # tokens
    filename_tokens: list[str] = []
    pathname_tokens: list[str] = []

    # explicit matches per thing (repetition increase assuredness)
    filename: DocumentAttrs | None = None
    pathname: DocumentAttrs | None = None
    element: DocumentAttrs | None = None
    parent: DocumentAttrs | None = None
    siblings: DocumentAttrs | None = None

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
