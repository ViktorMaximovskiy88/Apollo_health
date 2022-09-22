# noqa E501
import os
import pathlib
import re
from itertools import groupby
from urllib.parse import urlparse

import magic


def compile_date_rgx():
    date_formats = [
        r"^[0-9]{8}$",  # mmddyyyy
        r"(?<!\d|\/)[0-9]{4}[\/\-\.\|][0-9][0-9]?[\/\-\.\|][0-9][0-9]?(?!\d|\/)",  # yyyy-MM-dd with -, /, . or | # noqa
        r"(?<!\d|\/)[0-9][0-9]?[\/\-\.\|][0-9][0-9]?[\/\-\.\|](?:\d{4}|\d{2})(?!\d|\/)",  # dd-MM-yyyy, dd-mm-yy. With -, /, . or | # noqa
        r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec).? [0-9][0-9]?(?:st|nd|rd|th)?,? [0-9][0-9][0-9][0-9]",  # M d, yyyy # noqa
        r"(?<! \d|\w{2})[0-9][0-9]? (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec).? [0-9][0-9][0-9][0-9]",  # d M yyyy # noqa
        r"(?<! \d|\w{2})[0-9][0-9]? (January|February|March|April|May|June|July|August|September|October|November|December),? [0-9][0-9][0-9][0-9]",  # d M yyyy # noqa
        r"(January|February|March|April|May|June|July|August|September|October|November|December) [0-9][0-9]?(?:st|nd|rd|th)?,? [0-9][0-9][0-9][0-9]",  # M d, yyyy # noqa
        r"(?<!\d |\w{2})(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec).?,? [0-9][0-9]?(?!\d |\w{2})",  # M, dd # noqa
        r"(?<!\d |\w{2})(January|February|March|April|May|June|July|August|September|October|November|December),? [0-9][0-9]?(?!\d |\w{2})",  # M, dd # noqa
        r"(?<!\d |\w{2})(January|February|March|April|May|June|July|August|September|October|November|December),? [0-9][0-9][0-9][0-9]",  # M, yyyy # noqa
        r"(?<!\d |\w{2})(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec).?,? [0-9]{4}",  # M, yyyy # noqa
        r"(?<!\d|\/|-|\||\.)[0-9][0-9]?[\/\-\.\|]\d{2}(?!\d|\/|-|\||\.)",  # MM/yy with /, -, | or . # noqa
        r"(?<!\d|\/|-|\||\.)[0-9][0-9]?[\/\-\.\|]\d{4}(?!\d|\/|-|\||\.)",  # MM/yyyy with /, -, | or . # noqa
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
        r"revision": "last_updated_date",
        r"revised": "last_updated_date",
        r"revis": "last_updated_date",
        r"rev\.": "last_updated_date",
        r"current": "last_updated_date",
        r"reviewed on": "last_reviewed_date",
        r"reviewed date": "last_reviewed_date",
        r"reviewed as of": "last_reviewed_date",
        r"last review": "last_reviewed_date",
        r"recent review": "last_reviewed_date",
        r"next review": "next_review_date",
        r"annual review": "next_review_date",
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
    "text/csv": "csv",
    "text/plain": "txt",
    "application/octet-stream": "bin",
    "image/png": "png",
}
extension_to_mimetype_map = {v: k for k, v in mimetype_to_extension_map.items()}

supported_extensions = [*mimetype_to_extension_map.values()]
supported_mimetypes = [*extension_to_mimetype_map.values()]


def get_extension_from_path_like(path_like: str | None) -> str | None:
    if path_like is None:
        return None

    maybe_extension = pathlib.Path(os.path.basename(path_like))
    if maybe_extension:
        extension = maybe_extension.suffix[1:]
        if extension in supported_extensions:
            return extension


def get_extension_from_content_type(content_type: str | None) -> str | None:
    if content_type is None:
        return None

    return mimetype_to_extension_map.get(content_type) or None


def get_mimetype(file_path: str | None):
    if file_path is None:
        return None

    mime = magic.Magic(mime=True)
    return mime.from_file(file_path)


def get_extension_from_file_mimetype(file_path: str | None) -> str | None:
    if file_path is None:
        return None

    mimetype = get_mimetype(file_path)
    if not mimetype:
        return None

    return mimetype_to_extension_map.get(mimetype)


def unique_by_attr(items: list[any], attr: str) -> list[any]:
    return list(set([getattr(item, attr) for item in items]))


def sort_by_attr(items: list[any], attr: str):
    return sorted(items, key=lambda x: getattr(x, attr))


# so you have to sort first for groupby to work...
def group_by_attr(items: list[any], attr: str):
    sorted_items = sort_by_attr(items, attr)
    return groupby(sorted_items, lambda x: getattr(x, attr))


def compact(input: list[str]) -> list[str]:
    return list(filter(None, input))


def tokenize_url(url: str):
    parsed = urlparse(url)
    return parsed.path.split("/")


def tokenize_filename(filename: str):
    return compact(re.split(r"[^a-zA-Z0-9]", filename))


def tokenize_string(input: str):
    return compact(re.split(r"\s", input))


def jaccard(a: list, b: list):
    if len(a) + len(b) == 0:
        return 1
    intersection = len(list(set(a).intersection(b)))
    union = (len(a) + len(b)) - intersection
    return intersection / union
