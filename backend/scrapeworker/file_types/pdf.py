import os
import pathlib

from backend.scrapeworker.xpdf_wrapper import pdfinfo, pdftotext
from backend.scrapeworker.doc_type_classifier import classify_doc_type
from backend.scrapeworker.detect_lang import detect_lang
from backend.scrapeworker.effective_date import (
    extract_dates,
    select_effective_date,
)


def select_title(metadata, url):
    filename_no_ext = pathlib.Path(os.path.basename(url)).with_suffix("")
    title = metadata.get("Title") or metadata.get("Subject") or str(filename_no_ext)
    return title


async def parse_metadata(temp_path, url) -> dict[str, str]:
    metadata = await pdfinfo(temp_path)
    text = await pdftotext(temp_path)
    dates = extract_dates(text)
    effective_date = select_effective_date(dates)
    title = select_title(metadata, url)
    document_type, confidence = classify_doc_type(text)
    lang_code = detect_lang(text)

    return {
        "metadata": metadata,
        "dates": dates,
        "effective_date": effective_date,
        "title": title,
        "document_type": document_type,
        "confidence": confidence,
        "lang_code": lang_code,
    }
