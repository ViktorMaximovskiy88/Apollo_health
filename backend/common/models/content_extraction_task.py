from datetime import datetime
from typing import Any
from uuid import UUID

from beanie import Indexed, PydanticObjectId

from backend.common.core.enums import TaskStatus
from backend.common.models.base_document import BaseDocument, BaseModel


class FormularyDatum(BaseModel):
    score: float = 0
    code: str | None = None
    rxcui: str | None = None
    name: str | None = None
    tier: int = 0

    pa: bool = False
    pan: str | None = None

    cpa: bool = False
    cpan: str | None = None

    st: bool = False
    stn: str | None = None

    ql: bool = False
    qln: str | None = None

    sp: bool = False

    stpa: bool = False

    mb: bool = False

    sco: bool = False

    dme: bool = False

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, FormularyDatum):
            return False
        fields = FormularyDatum.__fields__.keys() - ["name", "score"]
        for field in fields:
            if getattr(self, field) != getattr(other, field):
                return False
        return True


class ContentExtractionResult(BaseDocument):
    content_extraction_task_id: Indexed(PydanticObjectId) | None = None  # type: ignore
    page: int
    row: int
    first_collected_date: datetime
    result: dict = {}
    translation: FormularyDatum | None = None
    add: bool = False
    remove: bool = False
    edit: PydanticObjectId | None = None
    hash: Indexed(bytes) | None = None  # type: ignore


class DeltaStats(BaseModel):
    added: int = 0
    removed: int = 0
    updated: int = 0
    total: int = 0

    def add_delta_stats(self, result: ContentExtractionResult):
        self.total += 1
        if result.add:
            self.added += 1
        if result.remove:
            self.removed += 1
        if result.edit:
            self.updated += 1


class ContentExtractionTask(BaseDocument):
    initiator_id: PydanticObjectId | None = None
    doc_document_id: PydanticObjectId | None = None

    worker_id: UUID | None = None
    queued_time: datetime
    start_time: datetime | None = None
    end_time: datetime | None = None
    error_message: str | None = None
    status: str = TaskStatus.QUEUED

    extraction_count: int = 0
    untranslated_count: int = 0
    header: list[str] | None = None
    delta: DeltaStats = DeltaStats()


class UpdateContentExtractionTask(BaseModel):
    worker_id: UUID | None = None
    queued_time: datetime | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    status: str | None = None

    extraction_count: int | None = None
