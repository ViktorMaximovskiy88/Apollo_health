import asyncio
import logging
import sys
from pathlib import Path

import typer
from beanie import PydanticObjectId

sys.path.append(str(Path(__file__).parent.joinpath("../..").resolve()))
from backend.common.db.init import init_db
from backend.common.services.lineage.core import LineageService

app = typer.Typer()
log = logging.getLogger(__name__)
lineage_service = LineageService(logger=logging)


async def _reprocess_lineage(site_id: str):
    await init_db()
    typer.secho(f"Processing lineage for {site_id}...", fg=typer.colors.GREEN)
    await lineage_service.reprocess_lineage_for_site(site_id)


async def _clear_lineage():
    await init_db()
    typer.secho("Clearing lineage for all sites...", fg=typer.colors.GREEN)
    await lineage_service.clear_all_lineage()


@app.command()
def lineage_reprocess(
    site_id: str = typer.Option(
        ...,
        help="Site Id of the site to lineage...",
    )
):
    typer.secho("Starting lineage process...", fg=typer.colors.GREEN)
    site_id = PydanticObjectId(site_id)
    asyncio.run(_reprocess_lineage(site_id))


@app.command()
def lineage_clear():
    asyncio.run(_clear_lineage())


if __name__ == "__main__":
    app()
