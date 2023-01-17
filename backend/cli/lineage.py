import logging
import sys
from pathlib import Path

import asyncclick as click
from beanie import PydanticObjectId

sys.path.append(str(Path(__file__).parent.joinpath("../..").resolve()))
from backend.common.db.init import init_db
from backend.common.models.doc_document import DocDocument
from backend.common.services.lineage.core import LineageService
from backend.common.services.tag_compare import TagCompare

log = logging.getLogger(__name__)


@click.group()
@click.pass_context
async def lineage(ctx):
    ctx.obj = {"lineage_service": LineageService(logger=log)}
    await init_db()


@lineage.command()
@click.pass_context
@click.option("--site-id", help="Site ID to reprocess", required=True, type=PydanticObjectId)
async def reprocess(ctx, site_id: PydanticObjectId):
    lineage_service: LineageService = ctx.obj["lineage_service"]
    log.info(f"Reprocessing lineage for site id {site_id}")
    await lineage_service.reprocess_lineage_for_site(site_id)


@lineage.command()
@click.pass_context
@click.option("--site-id", help="Site ID to reprocess", required=True, type=PydanticObjectId)
async def clear(ctx, site_id: PydanticObjectId):
    lineage_service: LineageService = ctx.obj["lineage_service"]
    log.info(f"Clearing lineage for site id {site_id}")
    await lineage_service.clear_lineage_for_site(site_id)


@lineage.command()
@click.pass_context
async def clear_all(ctx):
    lineage_service: LineageService = ctx.obj["lineage_service"]
    await lineage_service.clear_all_lineage()


@lineage.command()
@click.pass_context
@click.option(
    "--current-doc-id", help="Current doc to compare", required=True, type=PydanticObjectId
)
@click.option("--previous-doc-id", help="Prev doc to compare", required=True, type=PydanticObjectId)
async def compare_tags(ctx, current_doc_id: PydanticObjectId, previous_doc_id: PydanticObjectId):
    current_doc = await DocDocument.get(current_doc_id)
    prev_doc = await DocDocument.get(previous_doc_id)

    if not current_doc or not prev_doc:
        raise Exception("Document(s) not found")

    tag_compare = TagCompare()
    await tag_compare.execute_and_save(current_doc, prev_doc)
    log.info("Tag compare complete")
