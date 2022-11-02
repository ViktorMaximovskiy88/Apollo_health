import logging
import sys
from pathlib import Path

import asyncclick as click
from beanie import PydanticObjectId

sys.path.append(str(Path(__file__).parent.joinpath("../..").resolve()))
from backend.common.db.init import init_db
from backend.common.services.lineage.core import LineageService

log = logging.getLogger(__name__)
lineage_service = LineageService(logger=log)


@click.group()
async def lineage():
    await init_db()


@lineage.command()
@click.option("--site-id", help="Site ID to reprocess", required=True, type=PydanticObjectId)
async def reprocess(site_id: PydanticObjectId):
    log.info(f"Reprocessing lineage for site id {site_id}")
    await lineage_service.reprocess_lineage_for_site(site_id)


@lineage.command()
@click.option("--site-id", help="Site ID to reprocess", required=True, type=PydanticObjectId)
async def clear(site_id: PydanticObjectId):
    log.info(f"Clearing lineage for site id {site_id}")
    await lineage_service.clear_lineage_for_site(site_id)
