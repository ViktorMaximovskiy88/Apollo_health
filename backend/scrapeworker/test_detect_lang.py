from backend.scrapeworker.detect_lang import detect_lang

def test_english_text():
    english_text = "dogs and cats"
    lang_code = detect_lang(english_text)
    assert lang_code == "en"

def test_spanish_text():
    spanish_text = "perros y gatos"
    lang_code = detect_lang(spanish_text)
    assert lang_code == "es"

def test_multiple_text_en(caplog):
    # determined by volume
    multiple_text = "dogs and cats and other things perros y gatos"
    lang_code = detect_lang(multiple_text)
    assert lang_code == "en"

def test_multiple_text_es(caplog):
    # determined by volume
    multiple_text = "dogs and cats perros y gatos y otras cosas"
    lang_code = detect_lang(multiple_text)
    assert lang_code == "es"

def test_unsupported_text():
    italian_text = "piove a catinelle"
    lang_code = detect_lang(italian_text)
    assert lang_code is None
