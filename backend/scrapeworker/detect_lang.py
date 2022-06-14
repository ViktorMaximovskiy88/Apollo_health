import langid
import logging
from backend.common.core.enums import LangCode

# detects languages we care about
# unsupported langs are set to 'other'
# when we  error, set to 'unknown'
def detect_lang(text: str) -> LangCode:
    try:
        lang_codes = set(code.value for code in LangCode)
        lang_code, _ = langid.classify(text)

        return LangCode(lang_code) if lang_code in lang_codes else LangCode.Other
    except Exception as ex:
        logging.error(ex)
        return LangCode.Unknown
