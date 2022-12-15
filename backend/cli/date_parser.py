import logging
import sys
from pathlib import Path
from pprint import pprint

import aiofiles
import asyncclick as click

sys.path.append(str(Path(__file__).parent.joinpath("../..").resolve()))
from backend.scrapeworker.common.date_parser import DateParser
from backend.scrapeworker.common.utils import date_rgxs, label_rgxs

log = logging.getLogger(__name__)


@click.group()
@click.pass_context
@click.option("--type", help="Parser to use", default="default", type=str)
async def date_parser(ctx, type: str):
    if type == "default":
        ctx.obj = {"parser": DateParser(date_rgxs, label_rgxs)}
    else:
        raise Exception("No soup")


@date_parser.command()
@click.option("--file", help="File to parse", required=True, type=str)
@click.pass_context
async def parse(ctx, file: str):
    log.info(f"Parsing dates for {file}")
    parser = ctx.obj["parser"]
    async with aiofiles.open(file, mode="r") as file:
        text = await file.read()
    parser.extract_dates(text)
    result = parser.as_dict()
    pprint(result)
