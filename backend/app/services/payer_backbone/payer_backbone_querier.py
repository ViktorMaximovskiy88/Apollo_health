import asyncio
from datetime import datetime, timezone
from typing import Type

from beanie.odm.queries.find import FindMany
from pydantic import BaseModel

from backend.common.models.payer_backbone import (
    MCO,
    UMP,
    Benefit,
    BenefitManager,
    Channel,
    Formulary,
    PayerBackbone,
    PayerParent,
    Plan,
    PlanBenefit,
)
from backend.common.models.payer_family import PayerFamily


class ControlledLivesResponse(BaseModel):
    ControllerName: str
    MedicalLives: int | None
    TotalMedicalLives: int | None
    PharmacyLives: int | None
    TotalPharmacyLives: int | None
    Channel: str | None
    ControllerId: int


class PayerBackboneQuerier:
    def __init__(self, payer_info: PayerFamily, effective_date: str | None = None) -> None:
        self.payer_info = payer_info
        if effective_date:
            year, month, day = effective_date.split("-")
            self.effective_date = datetime(int(year), int(month), int(day))
        else:
            self.effective_date = datetime.now(tz=timezone.utc).replace(
                minute=0, second=0, microsecond=0
            )

    async def relevant_payer_ids_of_type(self, PayerClass: Type[PayerBackbone]) -> list[int]:
        plan_benefits = await self.construct_plan_benefit_query()
        return await self.convert_plans_to_ids_of_type(plan_benefits, PayerClass)

    async def convert_plans_to_ids_of_type(
        self, plan_benefits: FindMany[PlanBenefit], PayerClass: Type[PayerBackbone]
    ) -> list[int]:
        result_ids: set[int | None] = set()
        async for pb in plan_benefits:
            if PayerClass is Formulary:
                result_ids.add(pb.l_formulary_id)
            if PayerClass is PayerParent:
                result_ids.add(pb.l_parent_id)
            if PayerClass is MCO:
                result_ids.add(pb.l_mco_id)
            if PayerClass is BenefitManager:
                result_ids.add(pb.l_bm_id)
            if PayerClass is Plan:
                result_ids.add(pb.l_plan_id)
            if PayerClass is UMP:
                result_ids.add(pb.l_ump_id)

        return list(filter(None, result_ids))

    async def convert_formulary_ids_to_ump(self, result_ids: set[int | None]) -> set[int | None]:
        benefits = self.payer_info.benefits
        benefits.sort()
        ump_ids: set[int | None] = set()
        formulary_query = Formulary.find(self.effective({"l_id": {"$in": result_ids}}))
        async for formulary in formulary_query:
            if not benefits or Benefit.Medical in benefits:
                ump_ids.add(formulary.l_medical_ump_id)
            if not benefits or Benefit.Pharmacy in benefits:
                ump_ids.add(formulary.l_pharmacy_ump_id)

        return ump_ids

    async def construct_plan_benefit_query(self) -> FindMany[PlanBenefit]:
        query = PlanBenefit.find(self.effective())
        if self.payer_info.benefits:
            query = query.find({"benefit": {"$in": self.payer_info.benefits}})
        if self.payer_info.regions:
            query = query.find({"states": {"$in": self.payer_info.regions}})
        if self.payer_info.channels:
            query = query.find({"channel": {"$in": self.payer_info.channels}})
        if self.payer_info.plan_types:
            query = query.find({"plan_types": {"$in": self.payer_info.plan_types}})
        query = await self.payer_id_criteria(query)

        return query

    async def payer_id_criteria(self, query: FindMany[PlanBenefit]) -> FindMany[PlanBenefit]:
        payer_type = self.payer_info.payer_type
        payer_ids = self.payer_info.payer_ids
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
                query = query.find({"l_ump_id": {"$in": payer_ids}})

        return query

    def effective(self, args: dict = {}) -> dict:
        return args | {
            "start_date": {"$lte": self.effective_date},
            "end_date": {"$gt": self.effective_date},
        }

    async def lookup_controller(self, id: int):
        parent, pbm = await asyncio.gather(
            PayerParent.find_one(self.effective({"l_id": id})),
            BenefitManager.find_one(self.effective({"l_id": id})),
        )
        return parent or pbm

    def pretty_channel(self, channel: Channel):
        if channel == Channel.Commercial:
            return "Commercial"
        if channel == Channel.ManagedMedicaid:
            return "Managed Medicaid"
        if channel == Channel.HealthExchange:
            return "Health Exchange"
        if channel == Channel.Medicare:
            return "Medicare"
        if channel == Channel.StateMedicaid:
            return "State Medicaid"
        return None

    async def lives_by_controller(self) -> list[ControlledLivesResponse]:
        plan_benefits = await self.construct_plan_benefit_query()
        ccbl: dict[int, dict[Channel, dict[Benefit, int]]] = {}
        async for plan in plan_benefits:
            ccbl.setdefault(plan.l_controller_id, {})
            ccbl[plan.l_controller_id].setdefault(plan.channel, {})
            ccbl[plan.l_controller_id][plan.channel].setdefault(plan.benefit, 0)
            ccbl[plan.l_controller_id][plan.channel][plan.benefit] += plan.lives

        controller_ids = ccbl.keys()
        controllers = await asyncio.gather(*[self.lookup_controller(id) for id in controller_ids])

        controller_lives = []
        for controller in controllers:
            for (channel, bl) in ccbl[controller.l_id].items():
                medical_lives = bl.get(Benefit.Medical, 0)
                pharmacy_lives = bl.get(Benefit.Pharmacy, 0)
                tot_pharm_lives, tot_med_lives = await asyncio.gather(
                    PlanBenefit.find(
                        self.effective(
                            {
                                "l_controller_id": controller.l_id,
                                "benefit": Benefit.Pharmacy,
                                "channel": channel,
                            }
                        )
                    ).sum("lives"),
                    PlanBenefit.find(
                        self.effective(
                            {
                                "l_controller_id": controller.l_id,
                                "benefit": Benefit.Medical,
                                "channel": channel,
                            }
                        )
                    ).sum("lives"),
                )
                tot_pharm_lives = int(tot_pharm_lives) if tot_pharm_lives else 0
                tot_med_lives = int(tot_med_lives) if tot_med_lives else 0

                controller_lives.append(
                    ControlledLivesResponse(
                        ControllerName=controller.name,
                        PharmacyLives=pharmacy_lives,
                        TotalPharmacyLives=tot_pharm_lives,
                        MedicalLives=medical_lives,
                        TotalMedicalLives=tot_med_lives,
                        Channel=self.pretty_channel(channel),
                        ControllerId=controller.l_id,
                    )
                )
        controller_lives.sort(key=lambda c: (c.ControllerId, c.Channel))
        return controller_lives
