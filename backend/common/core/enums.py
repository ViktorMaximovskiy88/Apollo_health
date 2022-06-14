from enum import Enum


class LangCode(str, Enum):
    English = "en"
    Spanish = "es"
    Other = "other"
    Unknown = "unknown"

class CollectionMethod(str, Enum):
    Automated = "AUTOMATED"
    Manual = "MANUAL"


class Status(str, Enum):
    Queued = "QUEUED"
    Pending = "PENDING"
    InProgress = "IN_PROGRESS"
    Finished = "FINISHED"
    Canceling = "CANCELING"
    Canceled = "CANCELED"
    Failed = "FAILED"
