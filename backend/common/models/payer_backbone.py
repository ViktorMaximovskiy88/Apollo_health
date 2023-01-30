from datetime import datetime
from enum import Enum
from typing import ClassVar, Type, Union

import pymongo
from beanie import UnionDoc

from backend.common.models.base_document import BaseDocument


class PayerBackboneUnionDoc(UnionDoc):
    class Settings:
        name = "PayerBackbone"


class Benefit(str, Enum):
    Medical = "MEDICAL"
    Pharmacy = "PHARMACY"


class PlanType(str, Enum):
    ADAP = "ADAP"
    Employer = "EMPLOYER"
    Government = "GOVERNMENT"
    HDHPHIX = "HDHP_HIX"
    HMO = "HMO"
    HMOMedicaid = "HMO_MEDICAID"
    HMOHIX = "HMO_HIX"
    MA = "MA"
    MAPD = "MA_PD"
    MedicalGroup = "MEDICAL_GROUP"
    MedicareB = "MEDICARE_B"
    OtherInsurer = "OTHER_INSURER"
    PBMOffering = "PBM_OFFERING"
    PDP = "PDP"
    POS = "POS"
    POSHIX = "POS_HIX"
    PPO = "PPO"
    PPOHIX = "PPO_HIX"
    StateMedicaid = "STATE_MEDICAID"


class Channel(str, Enum):
    Commercial = "COMMERCIAL"
    HealthExchange = "HEALTH_EXCHANGE"
    ManagedMedicaid = "MANAGED_MEDICAID"
    Medicare = "MEDICARE"
    StateMedicaid = "STATE_MEDICAID"


class BenefitManagerType(str, Enum):
    Custom = "CUSTOM"
    National = "NATIONAL"
    Processor = "PROCESSOR"


class BenefitManagerControl(str, Enum):
    Claims = "CLAIMS"
    Controlled = "CONTROLLED"
    MA = "MA"
    MAC = "MAC"


class PlanBenefit(BaseDocument):
    payer_key: ClassVar[str] = "plan_benefit"
    start_date: datetime = datetime(1970, 1, 1)
    end_date: datetime = datetime(2038, 1, 1)
    l_plan_id: int
    l_ump_id: int
    l_controller_id: int
    benefit: Benefit
    lives: int = 0
    states: list[str] = []

    l_formulary_id: int | None = None
    l_mco_id: int | None = None
    l_parent_id: int | None = None
    l_bm_id: int | None = None
    type: PlanType
    channel: Channel
    is_national: bool = False

    class Settings:
        union_doc = PayerBackboneUnionDoc
        indexes = [
            [
                ("_class_id", pymongo.ASCENDING),
                ("l_id", pymongo.ASCENDING),
                ("start_date", pymongo.ASCENDING),
                ("end_date", pymongo.ASCENDING),
            ],
            [
                ("_class_id", pymongo.ASCENDING),
                ("l_controller_id", pymongo.ASCENDING),
                ("start_date", pymongo.ASCENDING),
                ("end_date", pymongo.ASCENDING),
            ],
            [
                ("_class_id", pymongo.ASCENDING),
                ("l_plan_id", pymongo.ASCENDING),
                ("start_date", pymongo.ASCENDING),
                ("end_date", pymongo.ASCENDING),
            ],
            [
                ("_class_id", pymongo.ASCENDING),
                ("l_formulary_id", pymongo.ASCENDING),
                ("start_date", pymongo.ASCENDING),
                ("end_date", pymongo.ASCENDING),
            ],
            [
                ("_class_id", pymongo.ASCENDING),
                ("l_mco_id", pymongo.ASCENDING),
                ("start_date", pymongo.ASCENDING),
                ("end_date", pymongo.ASCENDING),
            ],
            [
                ("_class_id", pymongo.ASCENDING),
                ("l_parent_id", pymongo.ASCENDING),
                ("start_date", pymongo.ASCENDING),
                ("end_date", pymongo.ASCENDING),
            ],
            [
                ("_class_id", pymongo.ASCENDING),
                ("l_bm_id", pymongo.ASCENDING),
                ("start_date", pymongo.ASCENDING),
                ("end_date", pymongo.ASCENDING),
            ],
            [
                ("_class_id", pymongo.ASCENDING),
                ("l_ump_id", pymongo.ASCENDING),
                ("start_date", pymongo.ASCENDING),
                ("end_date", pymongo.ASCENDING),
            ],
        ]


class Plan(BaseDocument):
    payer_key: ClassVar[str] = "plan"
    start_date: datetime = datetime(1970, 1, 1)
    end_date: datetime = datetime(2038, 1, 1)
    name: str
    l_id: int

    l_formulary_id: int | None = None
    l_mco_id: int | None = None
    l_parent_id: int | None = None
    l_bm_id: int | None = None
    type: PlanType
    channel: Channel
    is_national: bool = False
    pharmacy_lives: int = 0
    medical_lives: int = 0
    pharmacy_states: list[str] = []
    medical_states: list[str] = []
    l_pharmacy_controller_id: int | None = None
    l_medical_controller_id: int | None = None

    class Settings:
        union_doc = PayerBackboneUnionDoc


class Formulary(BaseDocument):
    payer_key: ClassVar[str] = "formulary"
    name: str
    l_id: int
    start_date: datetime = datetime(1970, 1, 1)
    end_date: datetime = datetime(2038, 1, 1)
    l_medical_ump_id: int | None = None
    l_pharmacy_ump_id: int | None = None

    class Settings:
        union_doc = PayerBackboneUnionDoc


class MCO(BaseDocument):
    payer_key: ClassVar[str] = "mco"
    name: str
    l_id: int
    start_date: datetime = datetime(1970, 1, 1)
    end_date: datetime = datetime(2038, 1, 1)

    class Settings:
        union_doc = PayerBackboneUnionDoc


class UMP(BaseDocument):
    payer_key: ClassVar[str] = "ump"
    benefit: Benefit
    name: str
    l_id: int
    legacy_policy_label: str | None = None
    start_date: datetime = datetime(1970, 1, 1)
    end_date: datetime = datetime(2038, 1, 1)

    class Settings:
        union_doc = PayerBackboneUnionDoc


class PayerParent(BaseDocument):
    payer_key: ClassVar[str] = "parent"
    name: str
    l_id: int
    start_date: datetime = datetime(1970, 1, 1)
    end_date: datetime = datetime(2038, 1, 1)

    class Settings:
        union_doc = PayerBackboneUnionDoc


class BenefitManager(BaseDocument):
    payer_key: ClassVar[str] = "bm"
    name: str
    type: BenefitManagerType | None = None
    control: BenefitManagerControl | None = None
    l_id: int
    start_date: datetime = datetime(1970, 1, 1)
    end_date: datetime = datetime(2038, 1, 1)

    class Settings:
        union_doc = PayerBackboneUnionDoc


PayerBackbone = Union[Plan, PayerParent, BenefitManager, UMP, MCO, Formulary]
payer_classes: list[Type[PayerBackbone]] = [
    Plan,
    PayerParent,
    BenefitManager,
    UMP,
    MCO,
    Formulary,
]
