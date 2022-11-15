from typing import Any

from backend.common.models.document import RetrievedDocument
from backend.common.models.site import FocusSectionConfig, ScrapeMethodConfiguration
from backend.scrapeworker.common.models import DownloadContext
from backend.scrapeworker.document_tagging.indication_tagging import indication_tagger
from backend.scrapeworker.document_tagging.taggers import Taggers
from backend.scrapeworker.document_tagging.therapy_tagging import therapy_tagger
from backend.scrapeworker.file_parsers import docx, html, pdf, text, xlsx

__all__ = ["docx", "xlsx", "pdf", "html", "text"]


async def parse_by_type(
    file_path: str,
    download: DownloadContext,
    scrape_method_config: ScrapeMethodConfiguration | None = None,
):
    # TODO use content_type
    file_extension = download.file_extension
    url = download.request.url
    link_text = download.metadata.link_text

    if file_extension == "pdf":
        return await pdf.PdfParse(file_path, url, link_text=link_text).parse()
    elif file_extension == "docx":
        return await docx.DocxParser(file_path, url, link_text=link_text).parse()
    elif file_extension == "xlsx":
        return await xlsx.XlsxParser(file_path, url, link_text=link_text).parse()
    elif file_extension == "html":
        return await html.HtmlParser(
            file_path,
            url,
            link_text=link_text,
            scrape_method_config=scrape_method_config,
        ).parse()
    elif file_extension in ["txt", "csv"]:
        return await text.TextParser(file_path, url, link_text=link_text).parse()
    else:
        # raise NotImplementedError(f"no parse for file ext {file_extension}")
        return None


async def get_tags(
    parsed_content: dict[str, Any],
    document: RetrievedDocument | None = None,
    focus_configs: list[FocusSectionConfig] | None = None,
):
    taggers = Taggers(indication=indication_tagger, therapy=therapy_tagger)
    (therapy_tags, url_therapy_tags, link_therapy_tags) = await taggers.therapy.tag_document(
        parsed_content["text"],
        parsed_content["document_type"],
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
        parsed_content["document_type"],
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
