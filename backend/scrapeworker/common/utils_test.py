import os

from backend.scrapeworker.common.utils import (
    compile_date_rgx,
    get_extension_from_content_type,
    get_extension_from_file_mimetype,
    get_extension_from_path_like,
    normalize_url,
)

current_path = os.path.dirname(os.path.realpath(__file__))
fixture_path = os.path.join(current_path, "__fixtures__")


def test_date_regexes_count():
    regexes = compile_date_rgx()
    assert len(regexes) == 13


def test_get_extension_from_path_like_none():
    result = get_extension_from_path_like(None)
    assert result is None


def test_get_extension_from_path_like_url():
    input = "https://www.google.com/artifact.pdf"
    result = get_extension_from_path_like(input)
    assert result == "pdf"


def test_get_extension_from_path_like_url_empty():
    input = "https://www.google.com/artifactpdf"
    result = get_extension_from_path_like(input)
    assert result is None


def test_get_extension_from_path_like_path():
    input = "/user/path/artifact.docx"
    result = get_extension_from_path_like(input)
    assert result == "docx"


def test_get_extension_from_path_like_path_empty():
    input = "/user/path/artifactdocx"
    result = get_extension_from_path_like(input)
    assert result is None


def test_get_extension_from_content_type_none():
    result = get_extension_from_content_type(None)
    assert result is None


def test_get_extension_from_content_type():
    input = "application/pdf"
    result = get_extension_from_content_type(input)
    assert result == "pdf"


def test_get_extension_from_content_type_non_match():
    input = "application/json"
    result = get_extension_from_content_type(input)
    assert result is None


def test_get_extension_from_file_mimetype_none():
    result = get_extension_from_file_mimetype(None)
    assert result is None


def test_get_extension_from_file_mimetype():
    file_path = os.path.join(fixture_path, "test.docx")
    result = get_extension_from_file_mimetype(file_path)
    assert result == "docx"


def test_get_extension_from_file_mimetype_non_match():
    file_path = os.path.join(fixture_path, "music.mp3")
    result = get_extension_from_file_mimetype(file_path)
    assert result is None


def test_normalize_url_noForwardSlash():
    base = "https://a.com"
    url1 = "Docs/test.xlsx"
    anchor1 = "_blank"
    anchor2 = None
    result = normalize_url(url1, anchor1, base)
    result1 = normalize_url(url1, anchor2, base)
    assert result == "https://a.com/Docs/test.xlsx"
    assert result1 == "https://a.com/Docs/test.xlsx"


def test_normalize_url_from_parent():
    base1 = "https://a.com/parent1"
    base2 = "https://a.com"
    url = "../test.xlsx"
    anchor = "_blank"
    result = normalize_url(url, anchor, base1)
    result2 = normalize_url(url, anchor, base2)
    assert result == "https://a.com/test.xlsx"
    assert result2 == "https://a.com/test.xlsx"


def test_normalize_url_with_forwardSlash():
    base = "https://a.com"
    url = "/Docs/test.xlsx"
    anchor = "_blank"
    result = normalize_url(url, anchor, base)
    assert result == "https://a.com/Docs/test.xlsx"


def test_normalize_url_with_oldUrlStyle():
    base = "https://a.com"
    url = "//a.com/Docs/test.xlsx"
    anchor = "_blank"
    anchor1 = None
    result = normalize_url(url, anchor, base)
    result1 = normalize_url(url, anchor1, base)
    assert result == "https://a.com/Docs/test.xlsx"
    assert result1 == "https://a.com/Docs/test.xlsx"


def test_normalize_url_with_unsecureUrl():
    base = "http://a.com"
    url = "http://a.com/Docs/test.xlsx"
    anchor = "_blank"
    anchor1 = None
    result = normalize_url(url, anchor, base)
    result1 = normalize_url(url, anchor1, base)
    assert result == "http://a.com/Docs/test.xlsx"
    assert result1 == "http://a.com/Docs/test.xlsx"


def test_normalize_url_with_securedUrl():
    base = "https://a.com"
    url = "https://a.com/Docs/test.xlsx"
    anchor = "_blank"
    anchor1 = None
    result = normalize_url(url, anchor, base)
    result1 = normalize_url(url, anchor1, base)
    assert result == "https://a.com/Docs/test.xlsx"
    assert result1 == "https://a.com/Docs/test.xlsx"
