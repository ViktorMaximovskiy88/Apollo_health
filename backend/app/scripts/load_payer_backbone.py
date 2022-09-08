import asyncio
import sys
from pathlib import Path

from openpyxl import load_workbook
from openpyxl.worksheet.worksheet import Worksheet

this_folder = Path(__file__).parent
sys.path.append(str(this_folder.joinpath("../../..").resolve()))
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
    PayerBackboneUnionDoc,
    PayerParent,
    Plan,
    PlanType,
)


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


async def load_payer_backbone():
    await PayerBackboneUnionDoc.get_motor_collection().delete_many({})

    xlsx_path = this_folder.joinpath("payer_backbone.xlsx")
    wb = load_workbook(str(xlsx_path))
    sheet: Worksheet = wb["Export"]  # type: ignore

    h = None
    plans, formularies, par_groups, parents, mcos, bms = (
        {},
        {},
        {},
        {},
        {},
        {},
    )
    for line in sheet.values:
        if not h:
            h = {v: i for i, v in enumerate(line)}
            continue

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

        if not plan_id:
            break
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
            medical_par_group_id = int(medical_par_group_id)
        except ValueError:
            medical_par_group_id = None
        try:
            pharmacy_par_group_id = int(pharmacy_par_group_id)
        except ValueError:
            pharmacy_par_group_id = None

        plans.setdefault(
            plan_id,
            Plan(
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
            formularies.setdefault(
                formulary_id,
                Formulary(
                    l_id=int(formulary_id),
                    name=formulary_name,
                    l_medical_ump_id=medical_par_group_id,
                    l_pharmacy_ump_id=pharmacy_par_group_id,
                ),
            )
        if medical_par_group_id and medical_par_group_name:
            par_groups.setdefault(
                medical_par_group_id,
                UMP(
                    l_id=int(medical_par_group_id),
                    name=medical_par_group_name,
                    benefit=Benefit.Medical,
                ),
            )
        if pharmacy_par_group_id:
            par_groups.setdefault(
                pharmacy_par_group_id,
                UMP(
                    l_id=int(pharmacy_par_group_id),
                    name=pharmacy_par_group_name,
                    benefit=Benefit.Pharmacy,
                ),
            )
        if parent_id:
            parents.setdefault(parent_id, PayerParent(l_id=parent_id, name=parent_name))
        if mco_id:
            mcos.setdefault(mco_id, MCO(l_id=mco_id, name=mco_name))
        if pbm_id:
            bms.setdefault(
                pbm_id,
                BenefitManager(
                    l_id=pbm_id,
                    name=pbm_name,
                    type=convert_bm_type(pbm_type),
                    control=convert_bm_control(pbm_control),
                ),
            )

    inserts = []
    for plan in plans.values():
        inserts.append(plan.insert())
    for formulary in formularies.values():
        inserts.append(formulary.insert())
    for par_group in par_groups.values():
        inserts.append(par_group.insert())
    for parent in parents.values():
        inserts.append(parent.insert())
    for mco in mcos.values():
        inserts.append(mco.insert())
    for bm in bms.values():
        inserts.append(bm.insert())

    await asyncio.gather(*inserts)


async def execute():
    await init_db()
    await load_payer_backbone()


if __name__ == "__main__":
    asyncio.run(execute())
