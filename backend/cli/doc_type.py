import logging
import sys
from pathlib import Path
from pprint import pprint

import asyncclick as click

sys.path.append(str(Path(__file__).parent.joinpath("../..").resolve()))
from backend.common.db.init import init_db
from backend.common.models.doc_document import DocDocument, PydanticObjectId
from backend.common.storage.client import TextStorageClient
from backend.scrapeworker.doc_type_matcher import DocTypeMatcher

log = logging.getLogger(__name__)


@click.group()
@click.pass_context
async def doc_type(ctx):
    await init_db()


@doc_type.command()
@click.option("--doc-doc-id", help="Text file to analyze for doc type", required=True, type=str)
@click.pass_context
async def match(ctx, doc_doc_id: PydanticObjectId):

    doc_storage = TextStorageClient()
    doc_doc = await DocDocument.get(doc_doc_id)
    if not doc_doc:
        log.error(f"DocDocument not found: id={doc_doc_id}")
        return

    location = doc_doc.locations[0]
    raw_text = doc_storage.read_utf8_object(f"{doc_doc.text_checksum}.txt")
    doc_type = DocTypeMatcher(raw_text, location.link_text, location.url, doc_doc.name).exec()
    pprint(doc_type)
