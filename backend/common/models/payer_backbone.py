from beanie import UnionDoc

from backend.common.models.base_document import BaseDocument


class PayerBackbone(UnionDoc, BaseDocument):
    name: str

    class Settings:
        name = "PayerBackbone"


class Plan(PayerBackbone):
    l_id: int
    l_formulary_id: int


class Formulary(PayerBackbone):
    l_id: int
    l_parent_id: int
    l_bm_id: int
    l_drug_list_id: int
    l_ump_id: int


class MCO(PayerBackbone):
    l_id: int
    l_parent_id: int


class UMP(PayerBackbone):
    l_id: int


class DrugList(PayerBackbone):
    l_id: int


class PayerParent(PayerBackbone):
    l_id: int


class BenefitManager(PayerBackbone):
    l_id: int
