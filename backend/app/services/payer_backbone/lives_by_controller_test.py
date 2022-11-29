from random import random

import pytest
import pytest_asyncio

from backend.app.services.payer_backbone.payer_backbone_querier import (
    ControlledLivesResponse,
    PayerBackboneQuerier,
)
from backend.app.services.payer_backbone.payer_backbone_querier_test import create_plan_benefits
from backend.common.db.init import init_db
from backend.common.models.payer_backbone import (
    BenefitManager,
    Channel,
    Formulary,
    PayerParent,
    Plan,
    PlanType,
)
from backend.common.models.payer_family import PayerFamily


@pytest_asyncio.fixture(autouse=True)
async def before_each_test():
    await init_db(mock=True, database_name=str(random()))


@pytest.mark.asyncio
async def test_lives_by_controller_parent():
    docs = [
        Plan(
            name="p1",
            l_id=1,
            type=PlanType.HMO,
            channel=Channel.Commercial,
            pharmacy_lives=1,
            medical_lives=100,
            l_medical_controller_id=10,
            l_formulary_id=1,
        ),
        Plan(
            name="p2",
            l_id=2,
            type=PlanType.HMO,
            channel=Channel.Commercial,
            pharmacy_lives=1,
            medical_lives=100,
            l_medical_controller_id=10,
            l_formulary_id=1,
        ),
        Formulary(name="f1", l_id=1, l_medical_ump_id=1, l_pharmacy_ump_id=1),
        PayerParent(name="parent1", l_id=10),
    ]
    [await doc.insert() for doc in docs]
    await create_plan_benefits()

    pbbq = PayerBackboneQuerier(PayerFamily(name="", channels=[Channel.Commercial]))
    formatted_controller = await pbbq.lives_by_controller()
    assert formatted_controller == [
        ControlledLivesResponse(
            ControllerName="parent1",
            MedicalLives=200,
            PharmacyLives=0,
            TotalMedicalLives=200,
            TotalPharmacyLives=0,
            Channel="Commercial",
            ControllerId=10,
        )
    ]


@pytest.mark.asyncio
async def test_lives_by_controller_bm():
    docs = [
        Plan(
            name="p1",
            l_id=1,
            type=PlanType.HMO,
            channel=Channel.Commercial,
            pharmacy_lives=1,
            l_pharmacy_controller_id=10,
            l_formulary_id=1,
        ),
        Plan(
            name="p2",
            l_id=2,
            type=PlanType.HMO,
            channel=Channel.Commercial,
            pharmacy_lives=1,
            l_pharmacy_controller_id=10,
            l_formulary_id=1,
        ),
        Formulary(name="f1", l_id=1, l_medical_ump_id=1, l_pharmacy_ump_id=1),
        BenefitManager(name="bm1", l_id=10),
    ]
    [await doc.insert() for doc in docs]
    await create_plan_benefits()

    pbbq = PayerBackboneQuerier(PayerFamily(name="", channels=[Channel.Commercial]))
    formatted_controller = await pbbq.lives_by_controller()
    assert formatted_controller == [
        ControlledLivesResponse(
            ControllerName="bm1",
            MedicalLives=0,
            PharmacyLives=2,
            TotalMedicalLives=0,
            TotalPharmacyLives=2,
            Channel="Commercial",
            ControllerId=10,
        )
    ]


@pytest.mark.asyncio
async def test_lives_by_controller_same_controller():
    docs = [
        Plan(
            name="p1",
            l_id=1,
            type=PlanType.HMO,
            channel=Channel.Commercial,
            pharmacy_lives=1,
            medical_lives=10,
            l_pharmacy_controller_id=10,
            l_medical_controller_id=10,
            l_formulary_id=1,
        ),
        Plan(
            name="p2",
            l_id=2,
            type=PlanType.HMO,
            channel=Channel.Commercial,
            pharmacy_lives=1,
            medical_lives=10,
            l_pharmacy_controller_id=10,
            l_medical_controller_id=10,
            l_formulary_id=1,
        ),
        Formulary(name="f1", l_id=1, l_medical_ump_id=1, l_pharmacy_ump_id=1),
        PayerParent(name="parent1", l_id=10),
    ]
    [await doc.insert() for doc in docs]
    await create_plan_benefits()

    pbbq = PayerBackboneQuerier(PayerFamily(name="", channels=[Channel.Commercial]))
    formatted_controller = await pbbq.lives_by_controller()
    assert formatted_controller == [
        ControlledLivesResponse(
            ControllerName="parent1",
            MedicalLives=20,
            PharmacyLives=2,
            TotalMedicalLives=20,
            TotalPharmacyLives=2,
            Channel="Commercial",
            ControllerId=10,
        )
    ]


@pytest.mark.asyncio
async def test_lives_by_controller_multi():
    docs = [
        Plan(
            name="p1",
            l_id=1,
            type=PlanType.HMO,
            channel=Channel.Commercial,
            pharmacy_lives=1,
            medical_lives=5,
            l_pharmacy_controller_id=10,
            l_medical_controller_id=11,
            l_formulary_id=1,
        ),
        Plan(
            name="p2",
            l_id=1,
            type=PlanType.HMO,
            channel=Channel.Commercial,
            pharmacy_lives=10,
            medical_lives=100,
            l_pharmacy_controller_id=11,
            l_medical_controller_id=10,
            l_formulary_id=1,
        ),
        Plan(
            name="p3",
            l_id=1,
            type=PlanType.HMO,
            channel=Channel.Commercial,
            pharmacy_lives=10,
            medical_lives=100,
            l_pharmacy_controller_id=10,
            l_medical_controller_id=11,
            l_formulary_id=1,
        ),
        Formulary(name="f1", l_id=1, l_medical_ump_id=1, l_pharmacy_ump_id=1),
        PayerParent(name="parent1", l_id=10),
        PayerParent(name="parent2", l_id=11),
    ]
    [await doc.insert() for doc in docs]
    await create_plan_benefits()

    pbbq = PayerBackboneQuerier(PayerFamily(name="", channels=[Channel.Commercial]))
    formatted_controller = await pbbq.lives_by_controller()
    assert formatted_controller == [
        ControlledLivesResponse(
            ControllerName="parent1",
            MedicalLives=100,
            PharmacyLives=11,
            TotalMedicalLives=100,
            TotalPharmacyLives=11,
            Channel="Commercial",
            ControllerId=10,
        ),
        ControlledLivesResponse(
            ControllerName="parent2",
            MedicalLives=105,
            PharmacyLives=10,
            TotalMedicalLives=105,
            TotalPharmacyLives=10,
            Channel="Commercial",
            ControllerId=11,
        ),
    ]
