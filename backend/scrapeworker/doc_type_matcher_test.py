from backend.common.core.enums import DocumentType
from backend.common.models.site import ScrapeMethodConfiguration
from backend.scrapeworker.doc_type_classifier import guess_doc_type
from backend.scrapeworker.doc_type_matcher import DocTypeMatcher


def test_contains():
    matcher = DocTypeMatcher(
        raw_text="raw_text", raw_link_text="raw_link_text", raw_url="raw_url", raw_name="raw_name"
    )
    result = matcher._contains("alphabet soup dog animal", ["dog", "cat", "turtle"])
    assert result is True


def test_not_contains():
    matcher = DocTypeMatcher(
        raw_text="raw_text", raw_link_text="raw_link_text", raw_url="raw_url", raw_name="raw_name"
    )
    result = matcher._not_contains("alphabet soup dog animal", ["dog", "cat", "turtle"])
    assert result is False

    result = matcher._not_contains("what is turtle now", ["dog", "cat", "turtle"])
    assert result is False

    result = matcher._not_contains("big cat lion", ["dog", "cat", "turtle"])
    assert result is False

    result = matcher._not_contains("lemur", ["dog", "cat", "turtle"])
    assert result is True


def test_guess_doc_type_searchable_site_doc():
    config = ScrapeMethodConfiguration(searchable=True)
    doc_type, confidence, doc_vectors, doc_type_match = guess_doc_type(
        "raw_text", "raw_link_text", "raw_url", "J1234", config
    )
    assert doc_type == DocumentType.MedicalCoverageList
    assert confidence == 1
    assert len(doc_vectors) == 1 and len(doc_vectors[0]) > 1
    assert doc_type_match is None


def test_guess_doc_type_searchable_site_not_doc():
    # not searchable and not matched; model will change and not mocking it
    config = ScrapeMethodConfiguration(searchable=True)
    _doc_type, confidence, doc_vectors, doc_type_match = guess_doc_type(
        "raw_text", "raw_link_text", "raw_url", "raw_name", config
    )
    assert doc_type_match is None
    assert confidence > 1
    assert len(doc_vectors) == 1 and len(doc_vectors[0]) > 1


def test_guess_doc_type_matcher():
    config = ScrapeMethodConfiguration(searchable=False)
    doc_type, confidence, doc_vectors, doc_type_match = guess_doc_type(
        "raw_text", "new to market", "raw_url", "raw_name", config
    )
    assert doc_type == DocumentType.NewToMarketPolicy
    assert confidence == 0.8
    assert len(doc_vectors) == 1 and len(doc_vectors[0]) > 1
    assert doc_type_match is not None
