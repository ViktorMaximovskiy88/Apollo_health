import json
import logging
import sys
from pathlib import Path

import aiofiles
import asyncclick as click

sys.path.append(str(Path(__file__).parent.joinpath("../..").resolve()))
from backend.scrapeworker.file_parsers.mupdf import MuPdfParse
from backend.scrapeworker.file_parsers.mupdf_smart import MuPdfSmartParse
from backend.scrapeworker.file_parsers.pdf import PdfParse

log = logging.getLogger(__name__)


@click.group()
@click.pass_context
@click.option("--file", help="File to parse", required=True, type=str)
@click.option("--type", help="Parser to use", default="default", type=str)
async def text_parser(ctx, file: str, type: str):
    if type == "mu-smart":
        ctx.obj = {"parser": MuPdfSmartParse(file_path=file, url=f"file://{file}")}
    elif type == "mu":
        ctx.obj = {"parser": MuPdfParse(file_path=file, url=f"file://{file}")}
    else:
        ctx.obj = {"parser": PdfParse(file_path=file, url=f"file://{file}")}


@text_parser.command()
@click.option("--stdout", help="Write to output file", default=False, type=bool)
@click.pass_context
async def parse(ctx, stdout: bool):
    parser = ctx.obj["parser"]
    type = ctx.parent.params["type"]
    file = ctx.parent.params["file"]

    text = await parser.get_text()
    if stdout:
        print(text)
    else:
        parsed_path = Path(file)
        output_file = parsed_path.parent / f"{parsed_path.stem}-{type}.txt"
        async with aiofiles.open(output_file, mode="w") as f:
            await f.writelines(text)
        print(f"File output to {output_file}")


@text_parser.command()
@click.option("--stdout", help="Write to stdout", default=False, type=bool)
@click.option("--raw", help="Raw or processed output", default=False, type=bool)
@click.pass_context
async def dump(
    ctx,
    stdout: bool,
    raw: bool,
):
    parser = ctx.obj["parser"]

    if raw:
        json_output = parser.get_structure_json()
    else:
        json_output = json.dumps(parser.parts, indent=4)

    if stdout:
        print(json_output)
    else:
        parsed_path = Path(ctx.parent.params["file"])
        type = ctx.parent.params["type"]
        format = "raw" if raw else "schema"
        output_file = parsed_path.parent / f"{parsed_path.stem}-{type}-{format}.json"
        async with aiofiles.open(output_file, mode="w") as f:
            await f.write(json_output)
        print(f"File output to {output_file}")
