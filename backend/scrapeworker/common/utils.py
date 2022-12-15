# noqa E501
import os
import pathlib
import re
import unicodedata
from html import unescape
from itertools import groupby
from urllib.parse import unquote, urljoin, urlparse

import magic


def compile_date_rgx():
    date_formats = [
        r"(?<!\d|[A-Za-z]|\/)[0-9]{4}[A-Za-z]{3}(?!\d|[A-Za-z]|\/)",  # yyyyMMM, i.e. 2020Dec # noqa
        r"(?<!\d|[\/\-\.])[0-9]{4}(?!\d|[\/\-\.])",  # yyyy
        r"(?<!\d)[0-9]{6}(?!\d)",  # mmYYYY or YYYYmm
        r"(?<!\d)[0-9]{8}(?!\d)",  # mmddyyyy yyyymmdd
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
        r"(?<!\d|\/|-|\||\.)[0-9][0-9]?\s?[\/\-\.\|]\d{4}(?!\d|\/|-|\||\.)",  # MM/yyyy with /, -, | or . # noqa
    ]
    return [re.compile(fmt, flags=re.IGNORECASE) for fmt in date_formats]


def compile_qtr_rgx():
    quarter_formats = [r"Q[1-4]", r"quarter of", r"quarter", r"qtr"]
    qtr_num_formats = [
        r"\b[1-4]\b",
        r"\b(1st|2nd|3rd|4th)\b",
        r"\b(first|second|third|fourth)\b",
    ]
    year_num = r"(?<!\d|[\/\-\.])[0-9]{4}(?!\d|[\/\-\.])"

    return (
        [re.compile(fmt, flags=re.IGNORECASE) for fmt in quarter_formats],
        [re.compile(fmt, flags=re.IGNORECASE) for fmt in qtr_num_formats],
        re.compile(year_num),
    )


def compile_label_rgx():
    label_hash = {
        r"effective": "effective_date",
        r"eff": "effective_date",
        r"expire": "end_date",
        r"end date": "end_date",
        r"ends": "end_date",
        r"through": "end_date",
        r"updated": "last_updated_date",
        r"updates": "last_updated_date",
        r"revision": "last_updated_date",
        r"revised": "last_updated_date",
        r"revis": "last_updated_date",
        r"rev\.": "last_updated_date",
        r"current": "last_updated_date",
        r"version": "last_updated_date",
        r"last res\.": "last_updated_date",
        r"reviewed": "last_reviewed_date",  # this may need to be narrowed back to 'reviewed on', etc
        r"last review": "last_reviewed_date",
        r"recent review": "last_reviewed_date",
        r"next review": "next_review_date",
        r"annual review": "next_review_date",
        r"next update": "next_update_date",
        r"publish": "published_date",
        r"posted": "published_date",
        r"print date": "published_date",
        r"\bv\.": "published_date",
        r"devised": "published_date",
        r"issued": "published_date",
        r"date of origin": "published_date",
    }
    label_rgxs = [re.compile(fmt, flags=re.IGNORECASE) for fmt in label_hash.keys()]
    return label_rgxs, label_hash


date_rgxs = compile_date_rgx()
label_rgxs = compile_label_rgx()
quarter_rgxs = compile_qtr_rgx()
digit_rgx = r"\b\d+\b"

# the builtin mimetype map is lacking some
mimetype_to_extension_map = {
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "xlsx",
    "application/vnd.ms-excel": "xls",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "application/msword": "doc",
    "application/pdf": "pdf",
    "text/html": "html",
    "text/csv": "csv",
    "text/plain": "txt",
    "application/octet-stream": "bin",
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


def sort_by_key(items: list[any], key: str):
    return sorted(items, key=lambda x: x[key])


# so you have to sort first for groupby to work...
def group_by_attr(items: list[any], attr: str):
    sorted_items = sort_by_attr(items, attr)
    return groupby(sorted_items, lambda x: getattr(x, attr))


# so you have to sort first for groupby to work...
def group_by_key(items: list[any], key: str):
    sorted_items = sort_by_key(items, key)
    return groupby(sorted_items, lambda x: x[key])


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
        return 0
    intersection = len(list(set(a).intersection(b)))
    union = (len(a) + len(b)) - intersection
    return intersection / union


def deburr(input: str = "") -> str:
    if input is None:
        return ""
    return unicodedata.normalize("NFKD", input).encode("ascii", "ignore").decode()


def normalize_spaces(input: str = "") -> str:
    if input is None:
        return ""
    return re.sub(r" +", " ", input)


# return meaningful chars
def scrub_string(input: str = "") -> str:
    if input is None:
        return ""
    return re.sub(r"[^A-Za-z0-9 ]+", " ", input).strip()


# maybe too much but we can break it out without boolean gating too
def normalize_string(input: str = "", html=False, url=True, lower=True, strip=True) -> str:
    # so much for types...
    if input is None:
        return ""
    # order matters, html can contain urls
    if html:
        input = unescape(input)
    if url:
        input = unquote(input)
    # remove or replace non-ascii; ® gets removed while ö is the is replaced by o
    input = deburr(input)
    # replace non meaningful chars with space; the space keeps word boundaries
    if strip:
        input = scrub_string(input)
        input = normalize_spaces(input)

    if lower:
        input = input.lower()
    # always trim
    return input.strip()


# cases '../abc' '/abc' 'abc' 'https://a.com/abc' 'http://a.com/abc' '//a.com/abc'
# anchor targets can change behavior
def normalize_url(base_url: str, target_url: str, base_tag_href: str | None = None) -> str:
    target_url = urljoin(base_tag_href, target_url)
    return urljoin(base_url, target_url)
