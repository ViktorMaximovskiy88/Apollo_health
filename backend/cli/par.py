import logging
import sys
from pathlib import Path

import asyncclick as click
import pandas as pd

sys.path.append(str(Path(__file__).parent.joinpath("../..").resolve()))
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
    df = pd.read_csv(file, skipinitialspace=True)

    for _index, row in df.iterrows():
        doc = await DocDocument.find_one(
            {
                "locations.url": row["DocumentUrl"],
            }
        )

        if doc and row["Checksum"].lower() != doc.checksum:
            update = await DocDocument.get_motor_collection().find_one_and_update(
                {"_id": doc.id},
                {"$set": {"previous_par_id": row["ParDocumentId"]}},
            )
            print(update["_id"], update.get("previous_par_id", None))


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
