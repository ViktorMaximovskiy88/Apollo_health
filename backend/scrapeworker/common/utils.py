import re


def compile_date_rgx():
    date_formats = [
        r"(?<!\d|\/|-)[0-9]{4}(\/|-)[0-9][0-9]?(\/|-)[0-9][0-9]?(?!\d|\/|-)",  # yyyy-MM-dd with - or /
        r"(?<!\d|\/|-)[0-9][0-9]?(\/|-)[0-9][0-9]?(\/|-)(?:\d{4}|\d{2})(?!\d|\/|-)",  # dd-MM-yyyy, dd-mm-yy. With - or /
        r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec).? [0-9][0-9]?, [0-9][0-9][0-9][0-9]",  # M d, yyyy
        r"[0-9][0-9]? (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec).? [0-9][0-9][0-9][0-9]",  # d M yyyy
        r"[0-9][0-9]? (January|February|March|April|May|June|July|August|September|October|November|December),? [0-9][0-9][0-9][0-9]",  # d M yyyy
        r"(January|February|March|April|May|June|July|August|September|October|November|December) [0-9][0-9]?, [0-9][0-9][0-9][0-9]",  # M d, yyyy
        r"(?<!\d |\w{2})(January|February|March|April|May|June|July|August|September|October|November|December),? [0-9][0-9][0-9][0-9]",  # M, yyyy
        r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec).?,? [0-9]{4}",  # M, yyyy
        r"(?<!\d|\/|-)[0-9][0-9]?(\/|-)(?:\d{4}|\d{2})(?!\d|\/|-)",  # MM/yy or MM/yyyy with / or -
    ]
    return [re.compile(fmt, flags=re.IGNORECASE) for fmt in date_formats]
