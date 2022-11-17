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
