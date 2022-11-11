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
    df = pd.read_csv(file)
    print(
        f"ParDocumentId, ParChecksum, ParEffectiveDate, ParPolicyId, Version?, SHDocDocId, SHchecksum, SHFinalEffectiveDate, SHLineageId"  # noqa
    )
    for _index, row in df.iterrows():
        doc = await DocDocument.find_one({"locations.url": row["DocumentUrl"]})
        if doc:
            version = "Last" if doc.checksum.lower() != row["Checksum"].lower() else "Same"
            print(
                f"{row['ParDocumentId']}, {row['Checksum']}, {row['EffectiveDate']}, {row['PolicyId']}, {version}, {doc.id}, {doc.checksum}, {doc.final_effective_date}, {doc.lineage_id}"  # noqa
            )
        else:
            print(
                f"{row['ParDocumentId']}, {row['Checksum']}, {row['EffectiveDate']}, {row['PolicyId']}, , , , , "  # noqa
            )


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
            if matched:
                df.loc[index, "ProposedDocType"] = matched.document_type
            df.loc[index, "LocationCount"] = len(doc.locations)
            df.loc[index, "Name"] = doc.name
            df.loc[index, "LinkText"] = location.link_text
            df.loc[index, "ExternalUrl"] = location.url
            df.loc[index, "CurrentDocType"] = doc.document_type

    df.to_csv(output_file)
