from typing import Union

from beanie import UnionDoc

from backend.common.models.base_document import BaseDocument


class PayerBackboneUnionDoc(UnionDoc):
    class Settings:
        name = "PayerBackbone"


class Plan(BaseDocument):
    payer_key = "plan"
    name: str
    l_id: int
    l_formulary_id: int

    class Settings:
        union_doc = PayerBackboneUnionDoc


class Formulary(BaseDocument):
    payer_key = "formulary"
    name: str
    l_id: int
    l_parent_id: int
    l_bm_id: int
    l_drug_list_id: int
    l_ump_id: int

    class Settings:
        union_doc = PayerBackboneUnionDoc


class MCO(BaseDocument):
    payer_key = "mco"
    name: str
    l_id: int
    l_parent_id: int

    class Settings:
        union_doc = PayerBackboneUnionDoc


class UMP(BaseDocument):
    payer_key = "ump"
    name: str
    l_id: int

    class Settings:
        union_doc = PayerBackboneUnionDoc


class DrugList(BaseDocument):
    payer_key = "druglist"
    name: str
    l_id: int

    class Settings:
        union_doc = PayerBackboneUnionDoc


class PayerParent(BaseDocument):
    payer_key = "parent"
    name: str
    l_id: int

    class Settings:
        union_doc = PayerBackboneUnionDoc


class BenefitManager(BaseDocument):
    payer_key = "bm"
    name: str
    l_id: int

    class Settings:
        union_doc = PayerBackboneUnionDoc


PayerBackbone = Union[Plan, PayerParent, BenefitManager, DrugList, UMP, MCO, Formulary]
