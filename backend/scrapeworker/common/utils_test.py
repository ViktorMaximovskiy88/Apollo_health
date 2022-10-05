import os

from backend.scrapeworker.common.utils import (
    compile_date_rgx,
    get_extension_from_content_type,
    get_extension_from_file_mimetype,
    get_extension_from_path_like,
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
