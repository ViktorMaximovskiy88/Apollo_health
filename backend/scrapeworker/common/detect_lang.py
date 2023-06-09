import cld3

from backend.common.core.enums import LangCode


# detects languages we care about
# unsupported langs are set to 'other'
# when we  error, set to 'unknown'
def detect_lang(text: str) -> LangCode:
    try:
        lang_codes = set(code.value for code in LangCode)
        language, probability, is_reliable, proportion = cld3.get_language(text)  # type: ignore

        return LangCode(language) if language in lang_codes else LangCode.Other
    except Exception:
        return LangCode.Unknown
