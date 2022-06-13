import pycld2 as cld2

from backend.common.core.enums import LangCode

def detect_lang(text: str) -> LangCode:
    lang_codes=set(code.value for code in LangCode)
    _isReliable, _textBytesFound, details = cld2.detect(text)

    # details can be multiple languages
    lang_code = None
    if len(details) > 0:
        language, lang_code, x, y = details[0]
    
    return lang_code if lang_code in lang_codes else None


