from backend.scrapeworker.common.detect_lang import detect_lang
from backend.common.core.enums import LangCode

def test_english_text():
    english_text = "dogs and cats"
    lang_code = detect_lang(english_text)
    assert lang_code == LangCode.English

def test_spanish_text():
    spanish_text = "perros y gatos"
    lang_code = detect_lang(spanish_text)
    assert lang_code == LangCode.Spanish

def test_multiple_text_en(caplog):
    # determined by volume
    multiple_text = "dogs and cats and other things perros y gatos"
    lang_code = detect_lang(multiple_text)
    assert lang_code == LangCode.English

def test_multiple_text_es(caplog):
    # determined by volume
    multiple_text = "dogs and cats perros y gatos y otras cosas"
    lang_code = detect_lang(multiple_text)
    assert lang_code == LangCode.Spanish

def test_unsupported_text():
    unsupported_text = "影響包含對氣候的變化以及自然資源的枯竭程度"
    lang_code = detect_lang(unsupported_text)
    assert lang_code == LangCode.Other

