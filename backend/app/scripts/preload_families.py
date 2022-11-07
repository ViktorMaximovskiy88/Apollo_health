import asyncio
import sys
from pathlib import Path

from beanie import PydanticObjectId
from openpyxl import load_workbook

from backend.app.routes.payer_backbone import payer_class

this_folder = Path(__file__).parent
sys.path.append(str(this_folder.joinpath("../../..").resolve()))
from backend.common.db.init import init_db
from backend.common.models.doc_document import DocDocument
from backend.common.models.document_family import DocumentFamily
from backend.common.models.payer_backbone import MCO, UMP, Benefit, Channel, PayerParent
from backend.common.models.payer_family import PayerFamily


def convert_backbone_level(level):
    if level == "MCO":
        return MCO.payer_key
    elif level == "UMP":
        return UMP.payer_key
    elif level == "Parent":
        return PayerParent.payer_key
    raise Exception(f"{level} is not a valid Payer Type!")


def convert_channel(channel):
    if not channel:
        return []
    channels = channel.split(",")
    clean_channels = []
    for c in channels:
        c = c.strip()
        if c == "Commercial":
            clean_channels.append(Channel.Commercial)
        elif c == "Health Exchange":
            clean_channels.append(Channel.HealthExchange)
        elif c == "Managed Medicaid":
            clean_channels.append(Channel.ManagedMedicaid)
        elif c == "Medicare":
            clean_channels.append(Channel.Medicare)
        elif c == "State Medicaid":
            clean_channels.append(Channel.StateMedicaid)
        elif c == "Managed Medicare":
            pass
        elif c:
            raise Exception(f"{c} is not avalid Channel!")
    return clean_channels


def convert_benefit(benefit):
    if not benefit:
        return []
    benefits = benefit.split(",")
    clean_benefits = []
    for c in benefits:
        if c == "Medical":
            clean_benefits.append(Benefit.Medical)
        elif c == "Pharmacy":
            clean_benefits.append(Benefit.Pharmacy)
        elif c:
            raise Exception(f"{c} is not avalid Channel!")
    return clean_benefits


async def convert_backbone_value(values: str | None, payer_type: str):
    if not values:
        return []

    clean_values = []
    PayerClass = payer_class(payer_type)  # type: ignore
    values = values.replace(", Inc.", "? Inc.")
    for value in values.split(","):
        value = value.strip().replace("? Inc.", ", Inc.")
        query = PayerClass.find()
        if value.endswith(" (Medical)"):
            query = PayerClass.find(
                {"name": value.removesuffix(" (Medical)"), "benefit": Benefit.Medical}
            )
        elif value.endswith(" (Rx)"):
            query = PayerClass.find(
                {"name": value.removesuffix(" (Rx)"), "benefit": Benefit.Pharmacy}
            )
        else:
            query = PayerClass.find(
                {
                    "name": value,
                }
            )
        payer = await query.find().to_list()
        if not payer:
            raise Exception(f"No match found for {payer_type}: '{value}'")
        if len(payer) > 1:
            raise Exception(f"Multiple matches found for {payer_type}: '{value}'")
        clean_values.append(payer[0].l_id)
    return clean_values


async def create_families():
    excel_path = this_folder.joinpath("Set 1 Load Files_v1.xlsx")
    wb = load_workbook(str(excel_path))

    pf_sheet = wb["load file Payer Family"]
    dc_doc_sheet = wb["load file Set 1 Doc Family"]
    pf_doc_sheet = wb["load file Set 1 Payer Family"]
    pf_by_name: dict[str, PayerFamily] = {}
    h = {}
    print("Start Payer Family Creation")
    updates = []

    async def create_pf(line):
        name = line[h["Name"]]
        payer_type = convert_backbone_level(line[h["Backbone Level"]])
        payer_ids = await convert_backbone_value(line[h["Backbone Value"]], payer_type)
        channels = convert_channel(line[h["Channel"]])
        benefits = convert_benefit(line[h["Benefits"]])
        pf = PayerFamily(
            name=name,
            payer_type=payer_type,
            payer_ids=payer_ids,
            channels=channels,
            benefits=benefits,
        )
        existing_pf = await PayerFamily.find_one({"name": pf.name})
        if existing_pf:
            pf.id = existing_pf.id
        else:
            pf.id = PydanticObjectId()
            await pf.save()
        pf_by_name[pf.name] = pf

    for line in pf_sheet.values:  # type: ignore
        if not h:
            h = {v: i for i, v in enumerate(line)}
            continue
        updates.append(create_pf(line))
    await asyncio.gather(*updates)
    print("Finish Payer Family Creation")

    async def update_document_payer(line):
        doc_id = PydanticObjectId(line[h["docdocument_id"]])
        site_id = PydanticObjectId(line[h["site_id"]])
        pf_name = str(line[h["Payer Family"]])
        pf = pf_by_name.get(pf_name)

        if not pf:
            raise Exception(f"No payer family found for: {pf_name}")

        doc = await DocDocument.get(doc_id)
        if not doc:
            raise Exception(f"{doc_id} DocDocument not found!")
        for loc in doc.locations:
            if loc.site_id == site_id:
                pass
            loc.payer_family_id = pf.id

        await doc.save()

    print("Start Payer Family Assignment")
    updates = []
    h = {}
    for line in pf_doc_sheet.values:  # type: ignore
        if not h:
            h = {v: i for i, v in enumerate(line)}
            continue
        updates.append(update_document_payer(line))
    await asyncio.gather(*updates)
    print("Finish Payer Family Assignment")

    par_auth_doc_family = DocumentFamily(
        name="PAR | Authorization Policy | Authorization Details",
        document_type="Authorization Policy",
        field_groups=["AUTHORIZATION_DETAILS"],
        legacy_relevance=["PAR"],
    )
    existing_auth = await DocumentFamily.find_one({"name": par_auth_doc_family.name})
    if existing_auth:
        par_auth_doc_family.id = existing_auth.id
    else:
        par_auth_doc_family.id = PydanticObjectId()
        await par_auth_doc_family.save()

    par_treat_req_family = DocumentFamily(
        name="PAR | Treatment Request Form | Authorization Details",
        document_type="Treatment Request Form",
        field_groups=["AUTHORIZATION_DETAILS"],
        legacy_relevance=["PAR"],
    )
    existing_treat = await DocumentFamily.find_one({"name": par_treat_req_family.name})
    if existing_treat:
        par_treat_req_family.id = existing_treat.id
    else:
        par_treat_req_family.id = PydanticObjectId()
        await par_treat_req_family.save()

    print("Start Document Family Assignment")

    async def update_document_doc_fam(line):
        doc_family_name = line[h["Document Family"]]
        df_id = None
        doc_id = PydanticObjectId(line[h["docdocument_id"]])

        if doc_family_name == par_auth_doc_family.name:
            df_id = par_auth_doc_family.id
        elif doc_family_name == par_treat_req_family.name:
            df_id = par_treat_req_family.id
        else:
            raise Exception(f"Invalid document family name: {doc_family_name}")

        doc = await DocDocument.get(doc_id)
        if not doc:
            raise Exception(f"DocDocument {doc_id} not found!")
        doc.document_family_id = df_id
        await doc.save()

    h = {}
    updates = []
    for line in dc_doc_sheet.values:  # type: ignore
        if not h:
            h = {v: i for i, v in enumerate(line)}
            continue
        updates.append(update_document_doc_fam(line))

    await asyncio.gather(*updates)
    print("Stop Document Family Assignment")


async def execute():
    await init_db()
    await create_families()


if __name__ == "__main__":
    asyncio.run(execute())
