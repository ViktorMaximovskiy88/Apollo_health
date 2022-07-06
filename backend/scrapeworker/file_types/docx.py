import os
import pathlib
import docx2txt
from docx import Document
from backend.scrapeworker.doc_type_classifier import classify_doc_type
from backend.scrapeworker.detect_lang import detect_lang
from backend.scrapeworker.effective_date import (
    extract_dates,
    select_effective_date,
)


def docx_text(temp_path: str):
    text = docx2txt.process(temp_path)
    return text


def docx_info(temp_path: str) -> dict[str, str]:
    doc = Document(temp_path)
    return {
        "title": doc.core_properties.title,
        "category": doc.core_properties.category,
        "subject": doc.core_properties.subject,
    }


def select_title(metadata, url):
    filename_no_ext = pathlib.Path(os.path.basename(url)).with_suffix("")
    title = (
        metadata["title"]
        or metadata["subject"]
        or metadata["category"]
        or str(filename_no_ext)
    )
    return title


async def parse_metadata(temp_path, url) -> dict[str, str]:
    metadata = docx_info(temp_path)
    text = docx_text(temp_path)
    dates = extract_dates(text)
    effective_date = select_effective_date(dates)
    title = select_title(metadata, url)
    document_type, confidence = classify_doc_type(text)
    lang_code = detect_lang(text)

    identified_dates = list(dates.keys())
    identified_dates.sort()

    return {
        "metadata": metadata,
        "identified_dates": identified_dates,
        "effective_date": effective_date,
        "title": title,
        "document_type": document_type,
        "confidence": confidence,
        "lang_code": lang_code,
    }
