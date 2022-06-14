import pycld2 as cld2
from backend.common.core.enums import LangCode

# detects languages we care about
# in the event of an unsupported lang or if we cant detect, we set to 'other'
def detect_lang(text: str) -> LangCode:
    lang_codes = set(code.value for code in LangCode)
    _is_reliable, _bytes_found, details = cld2.detect(text)

    # details is a tuple (docs not very explicit...)
    lang_code = None
    if len(details) > 0 and _is_reliable:
        language, lang_code, _confidence, _value = details[0]

    return LangCode(lang_code) if lang_code in lang_codes else LangCode.Other
