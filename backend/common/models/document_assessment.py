from datetime import datetime
from beanie import PydanticObjectId
from pydantic import BaseModel
from backend.common.models.base_document import BaseDocument

class Comment(BaseModel):
    user_id: PydanticObjectId
    time: datetime
    comment: str

class Triage(BaseModel):
    effective_date: datetime | None = None
    document_type: str | None = None
    document_lineage_id: PydanticObjectId | None = None
    comments: list[Comment] = []

class TriageUpdate(BaseModel):
    effective_date: datetime | None = None
    document_type: str | None = None
    document_lineage_id: PydanticObjectId | None = None
    comments: list[Comment] | None = None

class AssessmentLock(BaseModel):
    work_queue_id: PydanticObjectId
    user_id: PydanticObjectId
    expires: datetime

class AssessmentLockUpdate(BaseModel):
    work_queue_id: str | None = None
    user_id: PydanticObjectId | None = None
    expires: datetime | None = None

class DocumentAssessment(BaseDocument):
    name: str
    site_id: PydanticObjectId | None
    scrape_task_id: PydanticObjectId | None
    retrieved_document_id: PydanticObjectId | None
    triage_status: str = 'QUEUED'
    triage: Triage = Triage()
    locks: list[AssessmentLock] = []
    
class DocumentAssessmentUpdate(DocumentAssessment):
    name: str | None = None
    triage_status: str | None = None
    triage: Triage | None = None
    locks: list[AssessmentLock] | None = None