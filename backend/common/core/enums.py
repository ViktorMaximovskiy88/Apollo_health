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


class SearchableType(str, Enum):
    CPTCODES = "CPTCODES"
    JCODES = "JCODES"


class DocumentType(str, Enum):
    Authorization_Policy = "Authorization Policy"
    Treatment_Request_Form = "Treatment Request Form"
    Payer_Unlisted_Policy = "Payer Unlisted Policy"
    Covered_Treatment_List = "Covered Treatment List"
    Regulatory_Document = "Regulatory Document"
    Formulary = "Formulary"
    Internal_Resource = "Internal Resource"
    Formulary_Update = "Formulary Update"
    NCCN_Guideline = "NCCN Guideline"
    Restriction_List = "Restriction List"
    Review_Committee_Meetings = "Review Committee Meetings"
    Not_Applicable = "Not Applicable"
