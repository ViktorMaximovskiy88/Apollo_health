from backend.common.models.site import FocusTherapyConfig
from backend.scrapeworker.document_tagging.therapy_tagging import FocusChecker


class MockSpan:
    def __init__(self, text: str, start_char: int, end_char: int) -> None:
        self.text = text
        self.start_char = start_char
        self.end_char = end_char


def simple_focus_config():
    return FocusTherapyConfig(
        doc_type="Formulary",
        start_separator="Prior Authorization",
        end_separator="PA Indication",
        all_focus=False,
    )


test_text = """
    Prior Authorization Group ACITRETIN
    Drug Names ACITRETIN
    PA Indication Indicator All FDA-approved Indications, Some Medically-accepted Indications
    Age Restrictions
    Prior Authorization Group ADAPALENE
    Drug Names ADAPALENE, DIFFERIN
    PA Indication Indicator All FDA-approved Indications
    Other Criteria - AUSTEDO
"""


class TestFocusChecker:
    def test_get_focus_by_area(self):
        url = "www.test.com"
        link_text = "test"
        config = simple_focus_config()
        focus_checker = FocusChecker(test_text, [config], url, link_text)

        focus_spans = [MockSpan("ACITRETIN", 30, 38), MockSpan("ADAPALENE", 236, 245)]
        for span in focus_spans:
            focus = focus_checker.check_focus(span, 0)
            assert focus is True
        non_focus_span = MockSpan("AUSTEDO", 330, 340)
        focus = focus_checker.check_focus(non_focus_span, 0)
        assert focus is False

    def test_get_focus_by_link(self):
        url = "www.test.com"
        link_text = "Download Acitretin Approval"
        config = simple_focus_config()
        focus_checker = FocusChecker(test_text, [config], url, link_text)

        span = MockSpan("ACITRETIN", 330, 340)
        focus = focus_checker.check_focus(span, 0)
        assert focus is True
        non_focus_span = MockSpan("AUSTEDO", 330, 340)
        focus = focus_checker.check_focus(non_focus_span, 0)
        assert focus is False

    def test_get_focus_by_url(self):
        url = "www.test.com/approval/acitretin-form-download"
        link_text = None
        config = simple_focus_config()
        focus_checker = FocusChecker(test_text, [config], url, link_text)

        span = MockSpan("ACITRETIN", 330, 340)
        focus = focus_checker.check_focus(span, 0)
        assert focus is True
        non_focus_span = MockSpan("AUSTEDO", 330, 340)
        focus = focus_checker.check_focus(non_focus_span, 0)
        assert focus is False

    def test_get_focus_by_all_focus(self):
        url = "www.test.com"
        link_text = "Download"
        config = simple_focus_config()
        config.all_focus = True
        focus_checker = FocusChecker(test_text, [config], url, link_text)

        spans = [MockSpan("ACITRETIN", 330, 340), MockSpan("AUSTEDO", 1000, 2000)]
        for span in spans:
            focus = focus_checker.check_focus(span, 0)
            assert focus is True

    def test_no_start_separator(self):
        url = "www.test.com"
        link_text = "Download Austedo"
        config = simple_focus_config()
        config.start_separator = None
        focus_checker = FocusChecker(test_text, [config], url, link_text)

        span = MockSpan("AUSTEDO", 1000, 2000)
        focus = focus_checker.check_focus(span, 0)
        assert focus is True
        non_focus_span = MockSpan("ACITRETIN", 30, 38)
        focus = focus_checker.check_focus(non_focus_span, 0)
        assert focus is True

    def test_no_end_separator(self):
        url = "www.test.com"
        link_text = "Download"
        config = simple_focus_config()
        config.end_separator = None
        focus_checker = FocusChecker(test_text, [config], url, link_text)

        spans = [MockSpan("AUSTEDO", 330, 340), MockSpan("ACITRETIN", 30, 38)]
        for span in spans:
            focus = focus_checker.check_focus(span, 0)
            assert focus is True

        non_focus_span = MockSpan("ACITRETIN", 1, 10)
        focus = focus_checker.check_focus(non_focus_span, 0)

    def test_multiple_configs(self):
        url = "www.test.com"
        link_text = "Download"
        config = simple_focus_config()
        config.start_separator = "Restrictions"
        config.end_separator = "Group"
        config_two = simple_focus_config()
        focus_checker = FocusChecker(test_text, [config, config_two], url, link_text)

        spans = [
            MockSpan("ACITRETIN", 30, 38),
            MockSpan("Authorization", 190, 200),
        ]
        for span in spans:
            focus = focus_checker.check_focus(span, 0)
            assert focus is True

    def test_get_no_focus_areas(self):
        url = "www.test.com"
        link_text = "Download"
        config = simple_focus_config()
        config.start_separator = "No Match"
        focus_checker = FocusChecker(test_text, [config], url, link_text)

        spans = [
            MockSpan("AUSTEDO", 330, 340),
            MockSpan("ACITRETIN", 30, 38),
            MockSpan("ACITRETIN", 1, 10),
        ]
        for span in spans:
            focus = focus_checker.check_focus(span, 0)
            assert focus is False

    def test_no_config(self):
        url = "www.test.com"
        link_text = "Download Austedo"
        focus_checker = FocusChecker(test_text, [], url, link_text)

        span = MockSpan("AUSTEDO", 1000, 2000)
        focus = focus_checker.check_focus(span, 0)
        assert focus is True
        non_focus_span = MockSpan("ACITRETIN", 30, 38)
        focus = focus_checker.check_focus(non_focus_span, 0)
        assert focus is False

    def test_offset(self):
        # Test offset param in check_focus
        url = "www.test.com"
        link_text = "test"
        config = simple_focus_config()
        focus_checker = FocusChecker(test_text, [config], url, link_text)

        focus_spans = [MockSpan("ACITRETIN", 20, 28), MockSpan("ADAPALENE", 226, 235)]
        for span in focus_spans:
            focus = focus_checker.check_focus(span, 10)
            assert focus is True
        non_focus_span = MockSpan("AUSTEDO", 330, 340)
        focus = focus_checker.check_focus(non_focus_span, 10)
        assert focus is False
