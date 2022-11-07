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
lineage_service = LineageService(logger=log)


@click.group()
async def lineage():
    await init_db()


async def _run_tag_compare(current_id: PydanticObjectId, prev_id: PydanticObjectId):
    log.info("Running tag compare")
    current_doc = await DocDocument.get(current_id)
    prev_doc = await DocDocument.get(prev_id)

    if not current_doc or not prev_doc:
        raise Exception("Document(s) not found")

    tag_compare = TagCompare()
    final_ther_tags, final_indi_tags = await tag_compare.execute(current_doc, prev_doc)
    current_doc.therapy_tags = final_ther_tags
    current_doc.indication_tags = final_indi_tags
    await current_doc.save()
    log.info("Tag compare complete")


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


@lineage.command()
@click.option("--current-doc", help="Current doc to compare", required=True, type=PydanticObjectId)
@click.option("--prev-doc", help="Prev doc to compare", required=True, type=PydanticObjectId)
async def compare_tags(current_id: PydanticObjectId, prev_id: PydanticObjectId):
    # this command likely doesn't work yet.
    # haven't been able to update with the switch to click yet
    await _run_tag_compare(current_id, prev_id)
