from backend.scrapeworker.doc_type_matcher import DocTypeMatcher


def test_contains():
    matcher = DocTypeMatcher(raw_text="", raw_link_text="", raw_url="", raw_name="")
    result = matcher._contains("alphabet soup dog animal", ["dog", "cat", "turtle"])
    assert result is True


def test_not_contains():
    matcher = DocTypeMatcher(raw_text="", raw_link_text="", raw_url="", raw_name="")
    result = not matcher._contains("alphabet soup dog animal", ["dog", "cat", "turtle"])
    assert result is False

    result = not matcher._contains("what is turtle now", ["dog", "cat", "turtle"])
    assert result is False

    result = not matcher._contains("big cat lion", ["dog", "cat", "turtle"])
    assert result is False

    result = not matcher._contains("lemur", ["dog", "cat", "turtle"])
    assert result is True
