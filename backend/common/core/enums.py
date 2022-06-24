from enum import Enum

class LangCode(str, Enum):
    English = "en"
    Spanish = "es"
    Other = "other"
    Unknown = "unknown"

class CollectionMethod(str, Enum):
    Automated = "AUTOMATED"
    Manual = "MANUAL"