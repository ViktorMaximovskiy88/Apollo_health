import logging
import sys
from pathlib import Path

import asyncclick as click
import pandas as pd

sys.path.append(str(Path(__file__).parent.joinpath("../..").resolve()))
from pymongo import UpdateOne

from backend.common.db.init import init_db
from backend.common.models.doc_document import DocDocument, PydanticObjectId
from backend.scrapeworker.doc_type_matcher import DocTypeMatcher

log = logging.getLogger(__name__)


@click.group()
@click.pass_context
@click.option("--file", help="File to parse", required=True, type=str)
async def par(ctx, file: str):
    await init_db()


@par.command()
@click.pass_context
async def prev_par_ids(ctx):
    file = ctx.parent.params["file"]
    parsed_path = Path(file)
    output_file = parsed_path.parent / f"{parsed_path.stem}-proposed.csv"
    df = pd.read_csv(file, skipinitialspace=True)
    df["EffectiveDate"] = pd.to_datetime(df["EffectiveDate"])

    batch = []
    for index, row in df.iterrows():
        docs = (
            await DocDocument.find_many({"locations.url": row["DocumentUrl"]})
            .sort("-final_effective_date")
            .to_list()
        )

        if len(docs) >= 1:
            print(index)
            doc = docs[0]
            df.loc[index, "SH_EffectiveDate"] = doc.final_effective_date
            df.loc[index, "DateMatch"] = (
                "SH_GTE_PAR" if doc.final_effective_date >= row["EffectiveDate"] else "SH_LT_PAR"
            )
            df.loc[index, "SH_Checksum"] = doc.checksum
            df.loc[index, "SH_DocDocId"] = doc.id
            df.loc[index, "ChecksumMatch"] = (
                "Lastest" if row["Checksum"].lower() != doc.checksum else "Same"
            )

            if (
                doc.final_effective_date >= row["EffectiveDate"]
                and row["Checksum"].lower() != doc.checksum
            ):
                batch.append(
                    UpdateOne({"_id": doc.id}, {"$set": {"previous_par_id": row["ParDocumentId"]}})
                )

    logging.info(f"items pending bulk write -> {len(batch)}")
    result = await DocDocument.get_motor_collection().bulk_write(batch)
    logging.info(
        f"bulk_write -> acknowledged={result.acknowledged} matched_count={result.matched_count} modified_count={result.modified_count}"  # noqa
    )

    df.to_csv(output_file)


@par.command()
@click.pass_context
async def doc_type_validation(ctx):
    file = ctx.parent.params["file"]
    parsed_path = Path(file)
    output_file = parsed_path.parent / f"{parsed_path.stem}-proposed.csv"

    df = pd.read_csv(file)
    df["DocDocId"] = df["Url"].str.extract(r"([a-fA-F\d]{24})", expand=False).str.strip()

    for index, row in df.iterrows():
        doc = await DocDocument.get(PydanticObjectId(row["DocDocId"]))
        if doc:
            location = doc.locations[0]
            matched = DocTypeMatcher(
                raw_text="",
                raw_link_text=location.link_text,
                raw_url=location.url,
                raw_name=doc.name,
            ).exec()
            df.loc[index, "CurrentDocType"] = doc.document_type
            if matched:
                df.loc[index, "ProposedDocType"] = matched.document_type
            df.loc[index, "LocationCount"] = len(doc.locations)
            df.loc[index, "Name"] = doc.name
            df.loc[index, "LinkText"] = location.link_text
            df.loc[index, "ExternalUrl"] = location.url

    df.insert(0, "CurrentDocType", df.pop("CurrentDocType"))
    df.insert(1, "ExpectedDocType", df.pop("ExpectedDocType"))
    df.insert(2, "ProposedDocType", df.pop("ProposedDocType"))
    df.insert(3, "Name", df.pop("Name"))
    df.insert(4, "LinkText", df.pop("LinkText"))

    df.to_csv(output_file)
