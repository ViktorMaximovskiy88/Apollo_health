from backend.common.models.site import AttrSelector
from backend.scrapeworker.common.selectors import filter_by_hidden_value, filter_by_href, to_xpath


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


class TestToXpath:
    def test_base_selector(self):
        attr_selector = AttrSelector(attr_name="onclick")
        selector = to_xpath(attr_selector)
        assert selector == '//a[@*[contains(name(), "onclick")]]'

    def test_value_selector(self):
        attr_selector = AttrSelector(attr_name="onclick", attr_value="loadPdf")
        selector = to_xpath(attr_selector)
        assert selector == '//a[contains(@*[contains(name(), "onclick")], "loadPdf")]'

    def test_text_selector(self):
        attr_selector = AttrSelector(attr_name="onclick", has_text="Download")
        selector = to_xpath(attr_selector)
        assert selector == '//a[@*[contains(name(), "onclick")] and contains(text(), "Download")]'

    def test_all_selector(self):
        attr_selector = AttrSelector(attr_name="data-content", attr_value="/policy", has_text="Get")
        selector = to_xpath(attr_selector)
        assert (
            selector
            == '//a[contains(@*[contains(name(), "data-content")], "/policy") and contains(text(), "Get")]'  # noqa
        )

    def test_li_selector(self):
        attr_selector = AttrSelector(attr_element="li", attr_name="_ngcontent-uuw-c128")
        selector = to_xpath(attr_selector)
        assert selector == '//li[@*[contains(name(), "_ngcontent-uuw-c128")]]'

    def test_span_selector(self):
        attr_selector = AttrSelector(attr_element="span", attr_name="_ngcontent-uuw-c128")
        selector = to_xpath(attr_selector)
        assert selector == '//span[@*[contains(name(), "_ngcontent-uuw-c128")]]'

    def test_p_selector(self):
        attr_selector = AttrSelector(attr_element="p", attr_name="_ngcontent-uuw-c128")
        selector = to_xpath(attr_selector)
        assert selector == '//p[@*[contains(name(), "_ngcontent-uuw-c128")]]'

    def test_input_selector(self):
        attr_selector = AttrSelector(attr_element="input", attr_name="_ngcontent-uuw-c128")
        selector = to_xpath(attr_selector)
        assert selector == '//input[@*[contains(name(), "_ngcontent-uuw-c128")]]'
