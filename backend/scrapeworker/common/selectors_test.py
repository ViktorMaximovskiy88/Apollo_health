from backend.scrapeworker.common.selectors import filter_by_href, filter_by_hidden_value

# filter_by_href
def test_selector_href_javascript():
    selector = filter_by_href(javascript=True)
    assert selector == ['a[href^="javascript:"]']


def test_selector_href_javascript_extension():
    selector = filter_by_href(javascript=True, extensions=["pdf"])
    assert selector == ['a[href^="javascript:"]', 'a[href$=".pdf"]']


def test_selector_href_javascript_keyword():
    selector = filter_by_href(javascript=True, url_keywords=["dog"])
    assert selector == ['a[href^="javascript:"]', 'a[href*="dog"]']


def test_selector_href_extension_keyword():
    selector = filter_by_href(extensions=["pdf"], url_keywords=["dog"])
    assert selector == ['a[href$=".pdf"]', 'a[href*="dog"]']


def test_selector_href_javascript_extension_keyword():
    selector = filter_by_href(javascript=True, extensions=["pdf"], url_keywords=["dog"])
    assert selector == ['a[href^="javascript:"]', 'a[href$=".pdf"]', 'a[href*="dog"]']


def test_selector_href_extensions():
    selector = filter_by_href(extensions=["pdf", "docx"])
    assert selector == ['a[href$=".pdf"]', 'a[href$=".docx"]']


def test_selector_href_keywords():
    selector = filter_by_href(url_keywords=["dog", "cat"])
    assert selector == ['a[href*="dog"]', 'a[href*="cat"]']


# filter_by_hidden_value


def test_hidden_value_extension_keyword():
    selector = filter_by_hidden_value(extensions=["pdf"], url_keywords=["dog"])
    assert selector == [
        'input[type="hidden"][value$=".pdf"]',
        'input[type="hidden"][value*="dog"]',
    ]


def test_hidden_value_extensions():
    selector = filter_by_hidden_value(extensions=["pdf", "docx"])
    assert selector == [
        'input[type="hidden"][value$=".pdf"]',
        'input[type="hidden"][value$=".docx"]',
    ]


def test_hidden_value_keywords():
    selector = filter_by_hidden_value(url_keywords=["dog", "cat"])
    assert selector == [
        'input[type="hidden"][value*="dog"]',
        'input[type="hidden"][value*="cat"]',
    ]
