from random import random

import pytest
import pytest_asyncio

from backend.app.services.payer_backbone.payer_backbone_querier import PayerBackboneQuerier
from backend.common.db.init import init_db
from backend.common.models.document_family import PayerInfo
from backend.common.models.payer_backbone import (
    MCO,
    UMP,
    Benefit,
    BenefitManager,
    Channel,
    Formulary,
    PayerParent,
    Plan,
    PlanType,
)


@pytest_asyncio.fixture(autouse=True)
async def before_each_test():
    await init_db(mock=True, database_name=str(random()))
    plans: list[Plan] = [
        Plan(
            name="p1",
            l_id=1,
            l_formulary_id=1,
            l_parent_id=1,
            l_mco_id=1,
            l_bm_id=1,
            type=PlanType.MAPD,
            channel=Channel.Medicare,
            pharmacy_states=["CA", "MA"],
            medical_states=["CA", "MA"],
        ),
        Plan(
            name="p2",
            l_id=2,
            l_formulary_id=2,
            l_parent_id=1,
            l_mco_id=1,
            l_bm_id=1,
            type=PlanType.MAPD,
            channel=Channel.Medicare,
            pharmacy_states=["MA"],
            medical_states=[],
        ),
        Plan(
            name="p3",
            l_id=3,
            l_formulary_id=3,
            l_parent_id=2,
            l_mco_id=2,
            l_bm_id=1,
            type=PlanType.MAPD,
            channel=Channel.Medicare,
            pharmacy_states=["OH"],
            medical_states=["OH", "PA"],
        ),
        Plan(
            name="p4",
            l_id=4,
            l_formulary_id=4,
            l_parent_id=2,
            l_mco_id=2,
            l_bm_id=2,
            type=PlanType.HMO,
            channel=Channel.Commercial,
            pharmacy_states=["PA", "NV"],
            medical_states=["PA", "NV"],
        ),
    ]
    formularies: list[Formulary] = [
        Formulary(name="f1", l_id=1, l_pharmacy_ump_id=1, l_medical_ump_id=2),
        Formulary(name="f2", l_id=2, l_pharmacy_ump_id=1, l_medical_ump_id=2),
        Formulary(name="f3", l_id=3, l_pharmacy_ump_id=3, l_medical_ump_id=4),
        Formulary(name="f4", l_id=4, l_pharmacy_ump_id=5, l_medical_ump_id=6),
    ]
    umps: list[UMP] = [
        UMP(name="u1", l_id=1, benefit=Benefit.Pharmacy),
        UMP(name="u2", l_id=2, benefit=Benefit.Medical),
        UMP(name="u3", l_id=3, benefit=Benefit.Pharmacy),
        UMP(name="u4", l_id=4, benefit=Benefit.Medical),
        UMP(name="u5", l_id=5, benefit=Benefit.Pharmacy),
        UMP(name="u6", l_id=6, benefit=Benefit.Medical),
    ]
    parents: list[PayerParent] = [
        PayerParent(name="pt1", l_id=1),
        PayerParent(name="pt2", l_id=2),
    ]
    mcos: list[MCO] = [
        MCO(name="m1", l_id=1),
        MCO(name="m2", l_id=2),
    ]
    bms: list[BenefitManager] = [
        BenefitManager(name="bm1", l_id=1),
        BenefitManager(name="bm2", l_id=2),
    ]
    for pb in plans + formularies + umps + parents + mcos + bms:
        await pb.insert()


@pytest.mark.asyncio
async def test_querier_1():
    pi = PayerInfo(channels=[Channel.Commercial], benefits=[Benefit.Pharmacy])
    pbbq = PayerBackboneQuerier(pi)
    plans = await pbbq.construct_plan_query()
    plan_ids = [p.l_id async for p in plans]
    assert plan_ids == [4]

    plans = await pbbq.construct_plan_query()
    ump_ids = await pbbq.convert_plans_to_ids_of_type(plans, UMP)
    assert ump_ids == [5]

    formulary_ids = await pbbq.relevant_payer_ids_of_type(Formulary)
    assert formulary_ids == [4]


@pytest.mark.asyncio
async def test_querier_2():
    pi = PayerInfo(regions=["PA"])
    pbbq = PayerBackboneQuerier(pi)
    plan_ids = await pbbq.relevant_payer_ids_of_type(Plan)
    assert plan_ids == [3, 4]

    parent_ids = await pbbq.relevant_payer_ids_of_type(PayerParent)
    assert parent_ids == [2]


@pytest.mark.asyncio
async def test_querier_3():
    pi = PayerInfo(payer_type="formulary", payer_ids=["3"], benefits=[Benefit.Medical])
    pbbq = PayerBackboneQuerier(pi)
    ump_ids = await pbbq.relevant_payer_ids_of_type(UMP)
    assert ump_ids == [4]

    plan_ids = await pbbq.relevant_payer_ids_of_type(Plan)
    assert plan_ids == [3]
