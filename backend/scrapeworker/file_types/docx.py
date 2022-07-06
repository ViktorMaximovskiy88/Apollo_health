import docx2txt
from docx import Document


def docx_to_text(temp_path: str):
    text = docx2txt.process(temp_path)
    return text


def parse_metadata(temp_path: str, url: str | None = None) -> dict[str, str]:
    doc = Document(temp_path)
    return {
        "author": doc.core_properties.author,
        "category": doc.core_properties.category,
        "subject": doc.core_properties.subject,
    }
