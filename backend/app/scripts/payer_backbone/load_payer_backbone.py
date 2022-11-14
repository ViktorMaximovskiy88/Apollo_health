import asyncio
import dataclasses
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from openpyxl import load_workbook
from openpyxl.worksheet.worksheet import Worksheet

this_folder = Path(__file__).parent
sys.path.append(str(this_folder.joinpath("../../../..").resolve()))
from backend.common.db.init import init_db
from backend.common.models.payer_backbone import (
    MCO,
    UMP,
    Benefit,
    BenefitManager,
    BenefitManagerControl,
    BenefitManagerType,
    Channel,
    Formulary,
    PayerBackbone,
    PayerBackboneUnionDoc,
    PayerParent,
    Plan,
    PlanType,
)


@dataclass
class Delivery:
    plans: dict = field(default_factory=dict)
    formularies: dict = field(default_factory=dict)
    pump: dict = field(default_factory=dict)
    mump: dict = field(default_factory=dict)
    parents: dict = field(default_factory=dict)
    mcos: dict = field(default_factory=dict)
    bms: dict = field(default_factory=dict)


def convert_plan_type(type: str | None):
    if type == "ADAP":
        return PlanType.ADAP
    if type == "Employer":
        return PlanType.Employer
    if type == "Government":
        return PlanType.Government
    if type == "HDHP-HIX":
        return PlanType.HDHPHIX
    if type == "HMO":
        return PlanType.HMO
    if type == "HMO - Medicaid":
        return PlanType.HMOMedicaid
    if type == "HMO-HIX":
        return PlanType.HMOHIX
    if type == "MA":
        return PlanType.MA
    if type == "MA-PD":
        return PlanType.MAPD
    if type == "Medical Group":
        return PlanType.MedicalGroup
    if type == "Medicare B":
        return PlanType.MedicareB
    if type == "Other Insurer":
        return PlanType.OtherInsurer
    if type == "PBM Offering":
        return PlanType.PBMOffering
    if type == "PDP":
        return PlanType.PDP
    if type == "POS":
        return PlanType.POS
    if type == "POS-HIX":
        return PlanType.POSHIX
    if type == "PPO":
        return PlanType.PPO
    if type == "PPO-HIX":
        return PlanType.POS
    if type == "State Medicaid":
        return PlanType.StateMedicaid
    raise Exception(f"Plan Type: {type}")


def convert_channel(type: str | None):
    if type == "Commercial":
        return Channel.Commercial
    if type == "Health Exchange":
        return Channel.HealthExchange
    if type == "Managed Medicaid":
        return Channel.ManagedMedicaid
    if type == "Medicare":
        return Channel.Medicare
    if type == "State Medicaid":
        return Channel.StateMedicaid
    raise Exception(f"Channel: {type}")


def convert_bm_control(type: str | None):
    if type == "PBM Claims":
        return BenefitManagerControl.Claims
    if type == "PBM Controlled":
        return BenefitManagerControl.Controlled
    if type == "MA":
        return BenefitManagerControl.MA
    if type == "MAC":
        return BenefitManagerControl.MAC
    if not type:
        return None
    raise Exception(f"BM Control: {type}")


def convert_bm_type(type: str | None):
    if type == "Custom":
        return BenefitManagerType.Custom
    if type == "National":
        return BenefitManagerType.National
    if type == "Processor":
        return BenefitManagerType.Processor
    raise Exception(f"BM Type: {type}")


def process_line(h, line, start_date, delivery: Delivery):
    plan_id = line[h["Plan ID"]] or ""
    plan_name = line[h["Plan Name"]] or ""
    plan_type = line[h["Plan Type"]] or ""
    is_national_plan = line[h["National Plan"]] or ""
    channel = line[h["Channel"]] or ""
    formulary_id = line[h["Formulary ID"]] or ""
    formulary_name = line[h["Formulary Name"]] or ""
    pharmacy_par_group_id = line[h["Pharmacy PAR Group ID"]] or ""
    pharmacy_par_group_name = line[h["Pharmacy PAR Group Name"]] or ""
    medical_par_group_id = line[h["Medical PAR Group ID"]] or ""
    medical_par_group_name = line[h["Medical PAR Group Name"]] or ""
    parent_id = line[h["Parent ID"]] or ""
    parent_name = line[h["Parent Name"]] or ""
    mco_id = line[h["MCO ID"]] or ""
    mco_name = line[h["MCO Name"]] or ""
    pbm_id = line[h["PBM ID"]] or ""
    pbm_name = line[h["PBM Name"]] or ""
    pbm_type = line[h["PBMType"]]
    pbm_control = line[h["PBM Control"]]
    pharmacy_lives = line[h["Pharmacy Lives"]] or ""
    medical_lives = line[h["Medical Lives"]] or ""
    pharmacy_states = line[h["Pharm States"]] or ""
    medical_states = line[h["Medical States"]] or ""

    if not plan_id or plan_id == "No filters applied":
        return

    try:
        parent_id = int(parent_id)
    except ValueError:
        parent_id = None
    try:
        pbm_id = int(pbm_id)
    except ValueError:
        pbm_id = None
    try:
        mco_id = int(mco_id)
    except ValueError:
        mco_id = None
    try:
        medical_par_group_id = int(medical_par_group_id) * 10000
    except ValueError:
        medical_par_group_id = None
    try:
        pharmacy_par_group_id = int(pharmacy_par_group_id)
    except ValueError:
        pharmacy_par_group_id = None

    delivery.plans.setdefault(
        plan_id,
        Plan(
            start_date=start_date,
            l_id=int(plan_id),
            l_formulary_id=int(formulary_id),
            l_parent_id=parent_id,
            l_mco_id=mco_id,
            l_bm_id=pbm_id,
            name=plan_name,
            type=convert_plan_type(plan_type),
            is_national=bool(is_national_plan),
            channel=convert_channel(channel),
            pharmacy_lives=int(pharmacy_lives) if pharmacy_lives else 0,
            medical_lives=int(medical_lives) if medical_lives else 0,
            pharmacy_states=pharmacy_states.split(","),
            medical_states=medical_states.split(","),
        ),
    )
    if formulary_id:
        delivery.formularies.setdefault(
            formulary_id,
            Formulary(
                start_date=start_date,
                l_id=int(formulary_id),
                name=formulary_name,
                l_medical_ump_id=medical_par_group_id,
                l_pharmacy_ump_id=pharmacy_par_group_id,
            ),
        )
    if medical_par_group_id and medical_par_group_name:
        delivery.mump.setdefault(
            medical_par_group_id,
            UMP(
                start_date=start_date,
                l_id=int(medical_par_group_id),
                name=medical_par_group_name,
                benefit=Benefit.Medical,
            ),
        )
    if pharmacy_par_group_id:
        delivery.pump.setdefault(
            pharmacy_par_group_id,
            UMP(
                start_date=start_date,
                l_id=int(pharmacy_par_group_id),
                name=pharmacy_par_group_name,
                benefit=Benefit.Pharmacy,
            ),
        )
    if parent_id:
        delivery.parents.setdefault(
            parent_id, PayerParent(start_date=start_date, l_id=parent_id, name=parent_name)
        )
    if mco_id:
        delivery.mcos.setdefault(mco_id, MCO(start_date=start_date, l_id=mco_id, name=mco_name))
    if pbm_id:
        delivery.bms.setdefault(
            pbm_id,
            BenefitManager(
                start_date=start_date,
                l_id=pbm_id,
                name=pbm_name,
                type=convert_bm_type(pbm_type),
                control=convert_bm_control(pbm_control),
            ),
        )


async def insert_delivery(delivery: Delivery | None):
    if not delivery:
        return

    inserts = []
    for pfield in dataclasses.fields(Delivery):
        payers: dict[str, PayerBackbone | None] = getattr(delivery, pfield.name)
        for payer in payers.values():
            if payer:
                inserts.append(payer.insert())
    await asyncio.gather(*inserts)


def convert_filepath_to_start_date(filepath: str):
    if "4Q22" in filepath:
        return datetime(2022, 10, 1)
    if "3Q22" in filepath:
        return datetime(2000, 1, 1)
    raise Exception(f"Unknown start date time file {filepath}")


async def process_backbone(filepath: str, previous_delivery: Delivery | None):
    start_date = convert_filepath_to_start_date(filepath)
    wb = load_workbook(str(this_folder.joinpath(filepath)))
    sheet: Worksheet = wb["Export"]  # type: ignore

    h = None
    delivery = Delivery()
    for line in sheet.values:
        if not h:
            h = {v: i for i, v in enumerate(line)}
            continue

        process_line(h, line, start_date, delivery)

    if not previous_delivery:
        return delivery

    for pfield in dataclasses.fields(Delivery):
        payers: dict[str, PayerBackbone | None] = getattr(delivery, pfield.name)
        prev_payers: dict[str, PayerBackbone | None] = getattr(previous_delivery, pfield.name)
        prev_payers_ids = set(prev_payers.keys())
        for id, payer in payers.items():
            prev_payer = prev_payers.get(id, None)
            if id in prev_payers_ids:
                prev_payers_ids.remove(id)
            if not payer or not prev_payer:
                continue

            clean_prev = prev_payer.copy(exclude={"start_date", "end_date"})
            clean_payer = payer.copy(exclude={"start_date", "end_date"})
            if clean_prev != clean_payer:
                prev_payer.end_date = payer.start_date
            else:
                payers[id] = None

        # Deleted
        for id in prev_payers_ids:
            prev_payer = prev_payers.get(id, None)
            if not prev_payer:
                continue

            prev_payer.end_date = start_date

    await insert_delivery(previous_delivery)

    return delivery


async def load_payer_backbone():
    if await PayerBackboneUnionDoc.count():
        return

    previous_delivery = None
    for file in os.listdir(this_folder):
        if not file.endswith("xlsx"):
            continue
        previous_delivery = await process_backbone(file, previous_delivery)
    await insert_delivery(previous_delivery)


async def execute():
    await init_db()
    await load_payer_backbone()


if __name__ == "__main__":
    asyncio.run(execute())
