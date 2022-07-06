import os
import pathlib
import pandas as pd
from openpyxl import load_workbook
from backend.scrapeworker.doc_type_classifier import classify_doc_type
from backend.scrapeworker.detect_lang import detect_lang
from backend.scrapeworker.effective_date import (
    extract_dates,
    select_effective_date,
)


def xlsx_text(temp_path: str):
    dataframes = pd.read_excel(
        temp_path,
        engine="openpyxl",
        sheet_name=None,
    )
    text = ""
    for _key, df in dataframes.items():
        text += f"{df.to_string(index=False)}\n\n"
    return text


def xlsx_info(temp_path: str) -> dict[str, str]:
    workbook = load_workbook(temp_path)
    props = vars(workbook.properties)
    return props


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
    metadata = xlsx_info(temp_path)
    text = xlsx_text(temp_path)
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
