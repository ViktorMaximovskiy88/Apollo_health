import os
import re
import pathlib
import magic


def compile_date_rgx():
    date_formats = [
        r"(?<!\d|\/|-)[0-9]{4}(\/|-)[0-9][0-9]?(\/|-)[0-9][0-9]?(?!\d|\/|-)",  # yyyy-MM-dd with - or /
        r"(?<!\d|\/|-)[0-9][0-9]?(\/|-)[0-9][0-9]?(\/|-)(?:\d{4}|\d{2})(?!\d|\/|-)",  # dd-MM-yyyy, dd-mm-yy. With - or /
        r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec).? [0-9][0-9]?, [0-9][0-9][0-9][0-9]",  # M d, yyyy
        r"[0-9][0-9]? (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec).? [0-9][0-9][0-9][0-9]",  # d M yyyy
        r"[0-9][0-9]? (January|February|March|April|May|June|July|August|September|October|November|December),? [0-9][0-9][0-9][0-9]",  # d M yyyy
        r"(January|February|March|April|May|June|July|August|September|October|November|December) [0-9][0-9]?, [0-9][0-9][0-9][0-9]",  # M d, yyyy
        r"(?<!\d |\w{2})(January|February|March|April|May|June|July|August|September|October|November|December),? [0-9][0-9][0-9][0-9]",  # M, yyyy
        r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec).?,? [0-9]{4}",  # M, yyyy
        r"(?<!\d|\/|-)[0-9][0-9]?(\/|-)(?:\d{4}|\d{2})(?!\d|\/|-)",  # MM/yy or MM/yyyy with / or -
    ]
    return [re.compile(fmt, flags=re.IGNORECASE) for fmt in date_formats]


date_rgxs = compile_date_rgx()

# the builtin mimetype map is lacking some
mimetype_to_extension_map = {
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "xlsx",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "application/pdf": "pdf",
    "text/html": "html",
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
