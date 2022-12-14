from typing import Any

from backend.common.models.doc_document import DocDocument
from backend.common.models.site import FocusSectionConfig, ScrapeMethodConfiguration
from backend.scrapeworker.common.models import DownloadContext
from backend.scrapeworker.document_tagging.taggers import Taggers, indication_tagger, therapy_tagger
from backend.scrapeworker.file_parsers import docx, html, pdf, text, xlsx

__all__ = ["docx", "xlsx", "pdf", "html", "text"]
taggers = Taggers(indication=indication_tagger, therapy=therapy_tagger)


def get_parser_by_ext(file_extension: str):
    ParserClass = None
    if file_extension == "pdf":
        ParserClass = pdf.PdfParse
    elif file_extension == "docx":
        ParserClass = docx.DocxParser
    elif file_extension == "xlsx":
        ParserClass = xlsx.XlsxParser
    elif file_extension == "html":
        ParserClass = html.HtmlParser
    elif file_extension in ["txt", "csv"]:
        ParserClass = text.TextParser

    return ParserClass


async def parse_by_type(
    file_path: str,
    download: DownloadContext,
    scrape_method_config: ScrapeMethodConfiguration | None = None,
):
    # TODO use content_type
    file_extension = download.file_extension
    url = download.request.url
    link_text = download.metadata.link_text

    Parser = get_parser_by_ext(file_extension)
    if Parser:
        parser = Parser(
            file_path, url, link_text=link_text, scrape_method_config=scrape_method_config
        )
        result = await parser.parse()
        return result
    else:
        # raise NotImplementedError(f"no parse for file ext {file_extension}")
        return None


async def get_tags(
    parsed_content: dict[str, Any],
    document: DocDocument | None = None,
    focus_configs: list[FocusSectionConfig] | None = None,
):
    # if we have a doc use that doc type in the case its user edited
    doc_type = document.document_type if document else parsed_content["document_type"]
    (therapy_tags, url_therapy_tags, link_therapy_tags) = await taggers.therapy.tag_document(
        parsed_content["text"],
        doc_type,
        parsed_content["scrubbed_url"],
        parsed_content["scrubbed_link_text"],
        focus_configs,
        document,
    )
    (
        indication_tags,
        url_indication_tags,
        link_indication_tags,
    ) = await taggers.indication.tag_document(
        parsed_content["text"],
        doc_type,
        parsed_content["scrubbed_url"],
        parsed_content["scrubbed_link_text"],
        focus_configs,
        document,
    )

    parsed_content["therapy_tags"] = therapy_tags
    parsed_content["indication_tags"] = indication_tags
    parsed_content["url_therapy_tags"] = url_therapy_tags
    parsed_content["url_indication_tags"] = url_indication_tags
    parsed_content["link_therapy_tags"] = link_therapy_tags
    parsed_content["link_indication_tags"] = link_indication_tags
    return parsed_content
