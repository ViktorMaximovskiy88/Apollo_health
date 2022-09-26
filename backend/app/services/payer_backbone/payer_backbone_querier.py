from typing import Any, Type

from beanie.odm.queries.find import FindMany

from backend.common.models.document_family import PayerInfo
from backend.common.models.payer_backbone import (
    MCO,
    UMP,
    Benefit,
    BenefitManager,
    Formulary,
    PayerBackbone,
    PayerParent,
    Plan,
)


class PayerBackboneQuerier:
    def __init__(self, payer_info: PayerInfo, effective_date: str | None = None) -> None:
        self.payer_info = payer_info
        self.effective_date = effective_date

    async def relevant_payer_ids_of_type(self, PayerClass: Type[PayerBackbone]) -> list[int]:
        plans = await self.construct_plan_query()
        return await self.convert_plans_to_ids_of_type(plans, PayerClass)

    async def convert_plans_to_ids_of_type(
        self, plans: FindMany[Plan], PayerClass: Type[PayerBackbone]
    ) -> list[int]:
        result_ids: set[int | None] = set()
        async for plan in plans:
            if PayerClass is Formulary or PayerClass is UMP:
                result_ids.add(plan.l_formulary_id)
            if PayerClass is PayerParent:
                result_ids.add(plan.l_parent_id)
            if PayerClass is MCO:
                result_ids.add(plan.l_mco_id)
            if PayerClass is BenefitManager:
                result_ids.add(plan.l_bm_id)
            if PayerClass is Plan:
                result_ids.add(plan.l_id)

        if PayerClass is UMP:
            result_ids = await self.convert_formulary_ids_to_ump(result_ids)

        return list(filter(None, result_ids))

    async def convert_formulary_ids_to_ump(self, result_ids: set[int | None]) -> set[int | None]:
        benefits = self.payer_info.benefits
        benefits.sort()
        ump_ids: set[int | None] = set()
        async for formulary in Formulary.find({"l_id": {"$in": result_ids}}):
            if not benefits or Benefit.Medical in benefits:
                ump_ids.add(formulary.l_medical_ump_id)
            if not benefits or Benefit.Pharmacy in benefits:
                ump_ids.add(formulary.l_pharmacy_ump_id)

        return ump_ids

    async def construct_plan_query(self) -> FindMany[Plan]:
        query = Plan.find({})
        query = self.channel_criteria(query)
        query = self.plan_type_criteria(query)
        query = self.benefit_criteria(query)
        query = self.region_criteria(query)
        query = await self.payer_id_criteria(query)

        return query

    def channel_criteria(self, query: FindMany[Plan]) -> FindMany[Plan]:
        channels = self.payer_info.channels
        if channels:
            query = query.find({"channel": {"$in": channels}})
        return query

    def plan_type_criteria(self, query: FindMany[Plan]) -> FindMany[Plan]:
        plan_types = self.payer_info.plan_types
        if plan_types:
            query = query.find({"type": {"$in": plan_types}})
        return query

    def benefit_criteria(self, query: FindMany[Plan]) -> FindMany[Plan]:
        if self.payer_info.benefits:
            query = self.modify_query_by_benefit(query, {"benefit_states.0": {"$exists": True}})
        return query

    def region_criteria(self, query: FindMany[Plan]) -> FindMany[Plan]:
        regions = self.payer_info.regions
        if regions:
            query = self.modify_query_by_benefit(query, {"benefit_states": {"$in": regions}})
        return query

    def modify_query_by_benefit(self, query: FindMany, benefit_query: dict[str, Any]) -> FindMany:
        benefits = self.payer_info.benefits
        benefits.sort()

        medical, pharmacy = {}, {}
        for key, value in benefit_query.items():
            medical = {key.replace("benefit", "medical"): value}
            pharmacy = {key.replace("benefit", "pharmacy"): value}

        if not benefits or benefits == [Benefit.Medical, Benefit.Pharmacy]:
            query = query.find({"$or": [medical, pharmacy]})
        else:
            if Benefit.Medical in benefits:
                query = query.find(medical)
            if Benefit.Pharmacy in benefits:
                query = query.find(pharmacy)
        return query

    async def payer_id_criteria(self, query: FindMany[Plan]) -> FindMany[Plan]:
        payer_type = self.payer_info.payer_type
        payer_ids = self.payer_info.payer_ids
        benefits = self.payer_info.benefits
        benefits.sort()
        if payer_ids:
            payer_ids = list(map(int, payer_ids))
            if payer_type == "plan":
                query = query.find({"l_id": {"$in": payer_ids}})
            if payer_type == "formulary":
                query = query.find({"l_formulary_id": {"$in": payer_ids}})
            if payer_type == "mco":
                query = query.find({"l_mco_id": {"$in": payer_ids}})
            if payer_type == "parent":
                query = query.find({"l_parent_id": {"$in": payer_ids}})
            if payer_type == "bm":
                query = query.find({"l_bm_id": {"$in": payer_ids}})
            if payer_type == "ump":
                formulary_query = Formulary.find({})
                formulary_query = self.modify_query_by_benefit(
                    formulary_query, {"l_benefit_ump_id": {"$in": payer_ids}}
                )
                payer_ids = [f.l_id async for f in formulary_query]
                query = query.find({"l_formulary_id": {"$in": payer_ids}})

        return query
