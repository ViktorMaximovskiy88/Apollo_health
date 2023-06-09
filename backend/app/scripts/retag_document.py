import asyncio
import sys
from pathlib import Path

import typer
from beanie import PydanticObjectId

sys.path.append(str(Path(__file__).parent.joinpath("../../..").resolve()))
from backend.common.db.init import init_db
from backend.common.models.doc_document import DocDocument
from backend.common.models.document import RetrievedDocument
from backend.common.models.site import Site
from backend.common.storage.client import DocumentStorageClient, TextStorageClient
from backend.common.storage.hash import hash_full_text
from backend.scrapeworker.common.utils import normalize_string, tokenize_string
from backend.scrapeworker.doc_type_classifier import guess_doc_type
from backend.scrapeworker.document_tagging.indication_tagging import IndicationTagger
from backend.scrapeworker.document_tagging.therapy_tagging import TherapyTagger
from backend.scrapeworker.file_parsers import docx, html, pdf, text, xlsx


class ReTagger:
    def __init__(self):
        self.indication = IndicationTagger()
        self.therapy = TherapyTagger()

    async def retag_docs_on_site(self, site: Site, total: int = 0):
        async for doc in DocDocument.find({"locations.site_id": site.id}):
            await self.retag_document(doc, site, total)
            total += 1
        return total

    async def retag_document(self, doc: DocDocument, site: Site, total: int):
        rdoc = await RetrievedDocument.get(doc.retrieved_document_id)
        if not rdoc:
            return

        location = next(loc for loc in rdoc.locations if loc.site_id == site.id)

        document_type = rdoc.document_type or "N/A"
        link_text = normalize_string(location.link_text, url=False)
        url = normalize_string(location.url)
        doc_text = await self.get_text(doc, rdoc, url, link_text)

        is_searchable = site.scrape_method_configuration.searchable and len(doc.name) == 5
        _doc_type, _confidence, doc_vectors, doc_type_match = guess_doc_type(
            doc_text, location.link_text, location.url, doc.name, is_searchable
        )
        tokens = tokenize_string(doc_text)

        (therapy_tags, url_therapy_tags, link_therapy_tags) = await self.therapy.tag_document(
            doc_text, document_type, url, link_text, document=rdoc
        )
        (
            indication_tags,
            url_indication_tags,
            link_indication_tags,
        ) = await self.indication.tag_document(
            doc_text, document_type, url, link_text, document=rdoc
        )

        update = {
            "$set": {
                "therapy_tags": [t.dict() for t in therapy_tags],
                "indication_tags": [i.dict() for i in indication_tags],
                "doc_vectors": doc_vectors,
                "locations.$.url_therapy_tags": [t.dict() for t in url_therapy_tags],
                "locations.$.link_therapy_tags": [t.dict() for t in link_therapy_tags],
                "locations.$.url_indication_tags": [i.dict() for i in url_indication_tags],
                "locations.$.link_indication_tags": [i.dict() for i in link_indication_tags],
                "token_count": len(tokens),
                "doc_type_match": doc_type_match.dict() if doc_type_match else None,
            }
        }

        up1 = RetrievedDocument.get_motor_collection().find_one_and_update(
            {"_id": rdoc.id, "locations.site_id": site.id}, update
        )
        up2 = DocDocument.get_motor_collection().find_one_and_update(
            {"_id": doc.id, "locations.site_id": site.id}, update
        )
        await asyncio.gather(up1, up2)
        typer.secho(f"{total} Retagged '{doc.name}'")

    async def get_text(
        self,
        doc: DocDocument,
        rdoc: RetrievedDocument,
        url: str,
        link_text: str | None,
    ):
        text_client = TextStorageClient()
        file_extension = rdoc.file_extension
        txt_key = f"{rdoc.text_checksum}.txt"
        if text_client.object_exists(txt_key):
            return text_client.read_utf8_object(txt_key)

        doc_client = DocumentStorageClient()
        doc_key = f"{rdoc.checksum}.{file_extension}"
        with doc_client.read_object_to_tempfile(doc_key) as file_path:
            if file_extension == "pdf":
                ParserClass = pdf.PdfParse
            elif file_extension == "docx":
                ParserClass = docx.DocxParser
            elif file_extension == "xlsx":
                ParserClass = xlsx.XlsxParser
            elif file_extension == "html":
                ParserClass = html.HtmlParser
            else:
                ParserClass = text.TextParser
            doc_text = await ParserClass(file_path, url, link_text).get_text()

            text_hash = hash_full_text(doc_text)

            update = {"$set": {"text_checksum": text_hash}}
            up1 = RetrievedDocument.get_motor_collection().find_one_and_update(
                {"_id": rdoc.id}, update
            )
            up2 = DocDocument.get_motor_collection().find_one_and_update({"_id": doc.id}, update)
            await asyncio.gather(up1, up2)

            text_client.write_object_mem(f"{text_hash}.txt", bytes(doc_text, "utf-8"))

        return doc_text


if __name__ == "__main__":

    async def retag(site_id: str | None):
        await init_db()
        retagger = ReTagger()
        await retagger.indication.model()
        total = 0
        if site_id:
            site = await Site.get(PydanticObjectId(site_id))
            if not site:
                return
            typer.secho(f"Retagging documents from '{site.name}'")
            total = await retagger.retag_docs_on_site(site, total)
        else:
            async for site in Site.all():
                typer.secho(f"Retagging documents from '{site.name}'")
                total = await retagger.retag_docs_on_site(site, total)

    def start(site_id: str | None = None):
        asyncio.run(retag(site_id))

    typer.run(start)
