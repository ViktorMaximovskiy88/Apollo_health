import logging
import sys
from pathlib import Path

import asyncclick as click
import pandas as pd

sys.path.append(str(Path(__file__).parent.joinpath("../..").resolve()))
from backend.common.db.init import init_db
from backend.common.models.doc_document import DocDocument

log = logging.getLogger(__name__)


@click.group()
@click.pass_context
@click.option("--file", help="File to parse", required=True, type=str)
@click.option("--type", help="Parser to use", default="default", type=str)
async def par(ctx, file: str, type: str):
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
