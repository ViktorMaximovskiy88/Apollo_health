from backend.common.models.site import FocusSectionConfig, ScrapeMethodConfiguration
from backend.scrapeworker.common.models import DownloadContext
from backend.scrapeworker.file_parsers import docx, html, pdf, text, xlsx

__all__ = ["docx", "xlsx", "pdf", "html", "text"]


async def parse_by_type(
    file_path: str,
    download: DownloadContext,
    focus_config: list[FocusSectionConfig] | None = None,
    # TODO refactor and just pass scrape config?
    scrape_method_config: ScrapeMethodConfiguration | None = None,
):
    # TODO use content_type
    file_extension = download.file_extension
    url = download.request.url
    link_text = download.metadata.link_text

    if file_extension == "pdf":
        return await pdf.PdfParse(
            file_path, url, link_text=link_text, focus_config=focus_config
        ).parse()
    elif file_extension == "docx":
        return await docx.DocxParser(
            file_path, url, link_text=link_text, focus_config=focus_config
        ).parse()
    elif file_extension == "xlsx":
        return await xlsx.XlsxParser(
            file_path, url, link_text=link_text, focus_config=focus_config
        ).parse()
    elif file_extension == "html":
        return await html.HtmlParser(
            file_path,
            url,
            link_text=link_text,
            focus_config=focus_config,
            scrape_method_config=scrape_method_config,
        ).parse()
    elif file_extension in ["txt", "csv"]:
        return await text.TextParser(
            file_path, url, link_text=link_text, focus_config=focus_config
        ).parse()
    else:
        # raise NotImplementedError(f"no parse for file ext {file_extension}")
        return None
