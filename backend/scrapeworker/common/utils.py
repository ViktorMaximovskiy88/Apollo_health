# noqa E501
import os
import pathlib
import re

import magic


def compile_date_rgx():
    date_formats = [
        r"(?<!\d|\/)[0-9]{4}(\/|-|\.)[0-9][0-9]?(\/|-|\.)[0-9][0-9]?(?!\d|\/)",  # yyyy-MM-dd with -, / or .
        r"(?<!\d|\/)[0-9][0-9]?(\/|-|\.)[0-9][0-9]?(\/|-|\.)(?:\d{4}|\d{2})(?!\d|\/)",  # dd-MM-yyyy, dd-mm-yy. With -, / or .
        r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec).? [0-9][0-9]?,? [0-9][0-9][0-9][0-9]",  # M d, yyyy
        r"(?<! \d|\w{2})[0-9][0-9]? (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec).? [0-9][0-9][0-9][0-9]",  # d M yyyy
        r"(?<! \d|\w{2})[0-9][0-9]? (January|February|March|April|May|June|July|August|September|October|November|December),? [0-9][0-9][0-9][0-9]",  # d M yyyy
        r"(January|February|March|April|May|June|July|August|September|October|November|December) [0-9][0-9]?,? [0-9][0-9][0-9][0-9]",  # M d, yyyy
        r"(?<!\d |\w{2})(January|February|March|April|May|June|July|August|September|October|November|December),? [0-9][0-9][0-9][0-9]",  # M, yyyy
        r"(?<!\d |\w{2})(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec).?,? [0-9]{4}",  # M, yyyy
        r"(?<!\d|\/|-)[0-9][0-9]?(\/|-)\d{2}(?!\d|\/|-)",  # MM/yy with / or -
        r"(?<!\d|\/|-)[0-9][0-9]?(\/|-)\d{4}(?!\d|\/|-)",  # MM/yyyy with / or -
    ]
    return [re.compile(fmt, flags=re.IGNORECASE) for fmt in date_formats]


def compile_label_rgx():
    label_hash = {
        r"effective": "effective_date",
        r"eff": "effective_date",
        r"expire": "end_date",
        r"end date": "end_date",
        r"ends": "end_date",
        r"through": "end_date",
        r"updated": "last_updated_date",
        r"last updated": "last_updated_date",
        r"revision": "last_updated_date",
        r"revised": "last_updated_date",
        r"revis": "last_updated_date",
        r"rev\.": "last_updated_date",
        r"current": "last_updated_date",
        r"page updated": "last_updated_date",
        r"reviewed on": "last_reviewed_date",
        r"reviewed date": "last_reviewed_date",
        r"reviewed as of": "last_reviewed_date",
        r"last review": "last_reviewed_date",
        r"next review": "next_review_date",
        r"next update": "next_update_date",
        r"publish": "published_date",
        r"posted": "published_date",
        r"print date": "published_date",
        r"\bv\.": "published_date",
    }
    label_rgxs = [re.compile(fmt, flags=re.IGNORECASE) for fmt in label_hash.keys()]
    return label_rgxs, label_hash


date_rgxs = compile_date_rgx()
label_rgxs = compile_label_rgx()

# the builtin mimetype map is lacking some
mimetype_to_extension_map = {
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "xlsx",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "application/pdf": "pdf",
    "text/html": "html",
    "application/octet-stream": None,
}

extension_to_mimetype_map = {v: k for k, v in mimetype_to_extension_map.items()}


def get_extension_from_path_like(path_like: str | None) -> str | None:
    if path_like is None:
        return None

    maybe_extension = pathlib.Path(os.path.basename(path_like))
    if maybe_extension:
        extension = maybe_extension.suffix[1:]
        if extension in ["docx", "xlsx", "pdf", "html"]:
            return extension


def get_extension_from_content_type(content_type: str | None) -> str | None:
    if content_type is None:
        return None

    return mimetype_to_extension_map.get(content_type) or None


def get_extension_from_file_mime_type(file_path: str | None):
    if file_path is None:
        return None

    mime = magic.Magic(mime=True)
    mime_type = mime.from_file(file_path)
    return mimetype_to_extension_map.get(mime_type) or None
