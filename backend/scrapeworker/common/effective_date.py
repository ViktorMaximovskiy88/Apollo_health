from dateutil import parser
from datetime import datetime
import re


def extract_dates(text):
    dates: dict[datetime, int] = {}

    date_formats = [
        "[0-9]{4}-[0-9][0-9]?-[0-9][0-9]?",  # yyyy-MM-dd
        "[0-9]{4}/[0-9][0-9]?/[0-9][0-9]?",  # yyyy/MM/dd
        "[0-9][0-9]?-[0-9][0-9]?-[0-9]{4}",  # dd-MM-yyyy
        "[0-9][0-9]?/[0-9][0-9]?/[0-9]{4}",  # dd/MM/yyyy
        "(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec).? [0-9][0-9]?, [0-9][0-9][0-9][0-9]",  # M d, yyyy
        "[0-9][0-9]? (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec).? [0-9][0-9][0-9][0-9]",  # d M yyyy
        "[0-9][0-9]? (January|February|March|April|May|June|July|August|September|October|November|December),? [0-9][0-9][0-9][0-9]",  #d M yyyy
        "(January|February|March|April|May|June|July|August|September|October|November|December) [0-9][0-9]?, [0-9][0-9][0-9][0-9]",  # M d, yyyy
        "(January|February|March|April|May|June|July|August|September|October|November|December),? [0-9][0-9][0-9][0-9]",  # M d, yyyy
        "(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec).?,? [0-9]{4}",  # M, yyyy
        "[0-9][0-9]?/[0-9]{2}", # MM/yy
    ]
    date_rgxs = [re.compile(fmt, flags=re.IGNORECASE) for fmt in date_formats]
    for line in text.split("\n"):
        for i, rgx in enumerate(date_rgxs):
            match = rgx.finditer(line)
            if match:
                for m in match:
                    try:
                        datetext = m.group()
                        if i+1 == len(date_formats):
                            month, year = datetext.split('/')
                            datetext = f"20{year}-{month}-01"
                        if i+2 == len(date_formats):
                            pieces = datetext.split(r'[., ]')
                            datetext = f"20{pieces[-1]}-{pieces[0]}-01"

                        date = parser.parse(datetext)
                    except:
                        continue
                    dates.setdefault(date, 0)
                    dates[date] += 1
    return dates

def select_effective_date(dates: dict[datetime, int]) -> datetime | None:
    """
    Select effective date as the highest date not in the future
    """

    now = datetime.now()
    dates_in_the_past = list(filter(lambda d: now > d, dates.keys()))
    if dates_in_the_past:
        return max(dates_in_the_past)
    else:
        return None