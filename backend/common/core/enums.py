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
    PENDING = "PENDING"
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
    AuthorizationPolicy = "Authorization Policy"
    EvidenceOfCoverage = "Evidence of Coverage"
    ExclusionList = "Exclusion List"
    FeeSchedule = "Fee Schedule"
    Formulary = "Formulary"
    FormularyUpdate = "Formulary Update"
    InternalResource = "Internal Resource"
    LCD = "LCD"
    MedicalCoverageList = "Medical Coverage List"
    NCCNGuideline = "NCCN Guideline"
    NCD = "NCD"
    Newsletter = "Newsletter"
    NewToMarketPolicy = "New-to-Market Policy"
    NotApplicable = "Not Applicable"
    PayerUnlistedPolicy = "Payer Unlisted Policy"
    PreventiveDrugList = "Preventive Drug List"
    ProviderGuide = "Provider Guide"
    RegulatoryDocument = "Regulatory Document"
    RestrictionList = "Restriction List"
    ReviewCommitteeMeetings = "Review Committee Meetings"
    ReviewCommitteeSchedule = "Review Committee Schedule"
    SiteOfCarePolicy = "Site of Care Policy"
    SpecialtyList = "Specialty List"
    SummaryOfBenefits = "Summary of Benefits"
    TreatmentRequestForm = "Treatment Request Form"


class SectionType(str, Enum):
    THERAPY = "THERAPY"
    INDICATION = "INDICATION"
    KEY = "KEY"


class TagUpdateStatus(str, Enum):
    CHANGED = "CHANGED"
    ADDED = "ADDED"
    REMOVED = "REMOVED"
