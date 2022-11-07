import logging
import sys
from pathlib import Path

import aiofiles
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
async def data(ctx, file: str, type: str):
    await init_db()


@data.command()
@click.pass_context
async def match_docs(ctx):
    file = ctx.parent.params["file"]
    df = pd.read_csv(file)
    for _index, row in df.iterrows():
        doc = await DocDocument.find_one({"locations.url": row["url"]})
        if doc and doc.checksum != row["checksum"]:
            print(f"{row['policy_id']}, {row['checksum']}, {row['par_id']}, {doc.id}")
    print("/n")
