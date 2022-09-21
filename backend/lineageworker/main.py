import asyncio
import logging
import sys
from pathlib import Path

import typer
from beanie import PydanticObjectId

sys.path.append(str(Path(__file__).parent.joinpath("../..").resolve()))
from backend.common.db.init import init_db
from backend.common.services.lineage import LineageService

app = typer.Typer()
log = logging.getLogger(__name__)


async def _process(site_id: str):
    await init_db()
    lineage_service = LineageService(logger=logging)
    typer.secho(f"Processing lineage for {site_id}...", fg=typer.colors.GREEN)
    await lineage_service.reprocess_lineage_for_site(site_id)


@app.command()
def process(
    site_id: str = typer.Option(
        ...,
        help="Site Id of the site to lineage...",
    )
):
    typer.secho("Starting lineage process...", fg=typer.colors.GREEN)
    site_id = PydanticObjectId(site_id)
    asyncio.run(_process(site_id))


if __name__ == "__main__":
    app()
