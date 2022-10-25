import asyncio
import logging
import sys
from pathlib import Path
from pprint import pprint

import aiofiles
import typer
from beanie import PydanticObjectId

sys.path.append(str(Path(__file__).parent.joinpath("../..").resolve()))
from backend.scrapeworker.common.date_parser import DateParser
from backend.scrapeworker.common.utils import date_rgxs, label_rgxs
from backend.scrapeworker.file_parsers.mupdf import MuPdfParse

app = typer.Typer()
log = logging.getLogger(__name__)


# because our imports load all the models. i hate this, but dealwithit
async def init_lineage():
    from backend.common.db.init import init_db
    from backend.common.services.lineage.core import LineageService

    await init_db()
    return LineageService(logger=logging)


async def _lineage_reprocess(site_id: str):
    typer.secho(f"Processing lineage for {site_id}...", fg=typer.colors.GREEN)
    lineage_service = await init_lineage()
    await lineage_service.reprocess_lineage_for_site(site_id)


async def _lineage_clear():
    typer.secho("Clearing lineage for all sites...", fg=typer.colors.GREEN)
    lineage_service = await init_lineage()
    await lineage_service.clear_all_lineage()


async def _parse_dates(file: str):
    typer.secho(f"Parsing dates for {file}", fg=typer.colors.GREEN)
    parser = DateParser(date_rgxs, label_rgxs)
    async with aiofiles.open(file, mode="r") as file:
        text = await file.read()

    parser.extract_dates(text)
    result = parser.dump_dates()
    pprint(result)


async def _parse_text(file: str):

    parser = MuPdfParse(file_path=file, url=f"file://{file}")
    text = await parser.get_text()
    print(text)


@app.command()
def lineage_reprocess(
    site_id: str = typer.Option(
        ...,
        help="Site Id of the site to lineage...",
    )
):
    typer.secho("Starting lineage process...", fg=typer.colors.GREEN)
    site_id = PydanticObjectId(site_id)
    asyncio.run(_lineage_reprocess(site_id))


@app.command()
def lineage_clear():
    asyncio.run(_lineage_clear())


@app.command()
def parse_text(
    file: str = typer.Option(
        ...,
        help="Path of the text file to parse for dates",
    ),
):
    asyncio.run(_parse_text(file))


@app.command()
def parse_dates(
    file: str = typer.Option(
        ...,
        help="Path of the text file to parse for dates",
    )
):
    asyncio.run(_parse_dates(file))


if __name__ == "__main__":
    app()
