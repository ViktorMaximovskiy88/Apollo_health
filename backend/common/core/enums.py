from enum import Enum


class LangCode(str, Enum):
    English = "en"
    Spanish = "es"
    Other = "other"
    Unknown = "unknown"


class CollectionMethod(str, Enum):
    Automated = "AUTOMATED"
    Manual = "MANUAL"


class TaskStatus(str, Enum):
    QUEUED = "QUEUED"
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    FINISHED = "FINISHED"
    CANCELING = "CANCELING"
    CANCELED = "CANCELED"
    FAILED = "FAILED"


class BulkScrapeActions(str, Enum):
    CANCEL = "CANCEL"
    CANCEL_HOLD = "CANCEL-HOLD"
    HOLD = "HOLD"
    RUN = "RUN"


class ApprovalStatus(str, Enum):
    QUEUED = "QUEUED"
    APPROVED = "APPROVED"
    HOLD = "HOLD"


class SiteStatus(str, Enum):
    NEW = "NEW"
    QUALITY_HOLD = "QUALITY_HOLD"
    ONLINE = "ONLINE"
    INACTIVE = "INACTIVE"
