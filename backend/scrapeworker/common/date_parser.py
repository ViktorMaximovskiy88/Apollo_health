import logging
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Generator, Iterator

from dateutil import parser

from backend.scrapeworker.common.utils import quarter_rgxs

QTR_FMTS, QTR_NUM_FMTS, YEAR_FMT = quarter_rgxs


@dataclass
class LabelMatch:
    text: str
    priority: bool


class DateMatch:
    def __init__(
        self,
        date: datetime | None = None,
        match: re.Match[str] = None,
        last_date_index: int = None,
        rgx: int | None = None,
    ) -> None:
        self.date = date
        self.last_date_index = last_date_index
        self.start: int | None = None
        self.end: int | None = None
        self.label: LabelMatch | None = None
        self.rgx = rgx
        if match:
            self.start = match.start()
            self.end = match.end()

    def check_date_list(self, line: str):
        """If this date and last are separated by a comma, ignore last date"""
        if self.start is None or self.last_date_index is None:
            return
        accepted_range = 3
        if self.last_date_index == 0 or self.start - self.last_date_index > accepted_range:
            return
        separator_text = line[self.last_date_index : self.start]  # noqa: E203
        if re.fullmatch(r"\s*,\s*", separator_text):  # whitespace and 1 comma
            self.last_date_index = 0
        return

    def __str__(self):
        return str(self.date)


class DateParser:
    def __init__(
        self,
        date_rgxs: list[re.Pattern[str]],
        label_rgxs: tuple[list[re.Pattern[str]], dict[str, str]],
    ) -> None:
        self.date_rgxs = date_rgxs
        self.label_rgxs = label_rgxs
        self.whitespace_rgx = re.compile(r"\S")
        self.hyphen_rgx = re.compile(r"[\u2010-\u2015]|\u00AD|-")  # unicode hyphens
        self.effective_date = DateMatch()
        self.end_date = DateMatch()
        self.last_updated_date = DateMatch()
        self.last_reviewed_date = DateMatch()
        self.next_review_date = DateMatch()
        self.next_update_date = DateMatch()
        self.published_date = DateMatch()
        self.unclassified_dates: set[datetime] = set()
        self.heading_dates: list[DateMatch] = []

    NON_LABEL_RGX = [0, 2, 3, 14, 15]

    def dump_dates(self):
        return {
            "effective_date": str(self.effective_date),
            "end_date": str(self.end_date),
            "last_updated_date": str(self.last_updated_date),
            "last_reviewed_date": str(self.last_reviewed_date),
            "next_review_date": str(self.next_review_date),
            "next_update_date": str(self.next_update_date),
            "published_date": str(self.published_date),
            "unclassified_dates": [str(date) for date in self.unclassified_dates],
        }

    def exclude_text(self, text: str) -> bool:
        exclusions = ["omb approval"]
        lower_text = text.lower()
        for exclusion in exclusions:
            if exclusion in lower_text:
                return True
        return False

    def get_quarter_num(self, search_text: str):
        for i, rgx in enumerate(QTR_NUM_FMTS):
            qtr_match = rgx.search(search_text)
            if not qtr_match:
                continue
            quarter_text = qtr_match.group()
            if i <= 1:
                return quarter_text[0]
            if quarter_text.lower() == "first":
                return "1"
            if quarter_text.lower() == "second":
                return "2"
            if quarter_text.lower() == "third":
                return "3"
            if quarter_text.lower() == "fourth":
                return "4"

    def get_year_num(self, search_text: str):
        year_match = YEAR_FMT.search(search_text)
        if year_match:
            return year_match.group()

    def get_quarter_marker(self, text: str):
        for i, rgx in enumerate(QTR_FMTS):
            match = rgx.finditer(text)
            for m in match:
                quarter: str | None = None
                quarter_text = m.group()
                if i == 0:
                    # we've got the quarter
                    quarter = quarter_text[1]
                else:
                    # search for quarter before
                    start = 0 if m.start() - 7 < 0 else m.start() - 7
                    search_text = text[start : m.start()]  # noqa: E203
                    quarter = self.get_quarter_num(search_text)
                if not quarter:
                    # search for quarter after
                    end = m.end() + 5
                    search_text = text[m.end() : end]  # noqa: E203
                    quarter = self.get_quarter_num(search_text)
                yield quarter, m

    def construct_quarter_date(self, year: str, quarter: str):
        year_num, month_num, day_num = int(year), (int(quarter) * 3) - 2, 1
        if self.valid_range(month=month_num, year=year_num, day=day_num):
            date_text = f"{year_num}-{month_num}-{day_num}"
            date = parser.parse(date_text, ignoretz=True)
            return date

    def check_quarter_text(self, text: str):
        """Find 1st Quarter 20XX dates or similar"""
        for quarter, m in self.get_quarter_marker(text):
            year: str | None = None
            if quarter:
                # search for year after
                end = m.end() + 8
                search_text = text[m.end() : end]  # noqa: E203
                year = self.get_year_num(search_text)
                if not year:
                    # search for year before
                    start = 0 if m.start() - 8 < 0 else m.start() - 8
                    search_text = text[start : m.start()]  # noqa: E203
                    year = self.get_year_num(search_text)
            if year and quarter:
                date = self.construct_quarter_date(year, quarter)
                if not date:
                    continue
                return DateMatch(date, m)

    def get_doc_label_dates(self, label_texts: list[str]):
        best_match: DateMatch | None = None
        for text in label_texts:
            for quarter, m in self.get_quarter_marker(text):
                year = self.get_year_num(text)
                if not quarter or not year:
                    continue
                date = self.construct_quarter_date(year, quarter)
                if not date:
                    continue
                self.unclassified_dates.add(date)
                return DateMatch(date, m)
            for m in self.get_dates(text, rgx_excludes=self.NON_LABEL_RGX):
                self.unclassified_dates.add(m.date)
                if self.is_best_effective(m, best_match):
                    best_match = m
        return best_match

    def check_effective_date(self, label_texts: list[str]):
        if label_date := self.get_doc_label_dates(label_texts):
            # search other texts for dates. if found, assign as effective
            self.effective_date = label_date
        elif self.heading_dates:
            # if heading dates, get best effective and set to effective
            best_match: DateMatch | None = None
            for match in self.heading_dates:
                if self.is_best_effective(match, best_match):
                    best_match = match
            if best_match is not None:
                self.effective_date = best_match
        elif len(self.unclassified_dates) == 1 and self.effective_date.date is None:
            eff_date = list(self.unclassified_dates)[0]
            if self.end_date.date == eff_date:
                return
            self.effective_date = DateMatch(date=eff_date)

    def get_date_label(self, line: str, start: int, end: int, target="END") -> LabelMatch | None:
        """
        Find date label between start and end indexes of given string.
        If multiple labels found, returns the label found closest to the `target` index.
        """

        def check_match(match: Iterator[re.Match], closest_match: int, matched_label: str | None):
            for m in match:
                if target == "END" and m.end() >= closest_match:
                    closest_match = m.end()
                    matched_label = label_hash[rgx.pattern]
                elif target == "START" and m.start() <= closest_match:
                    closest_match = m.start()
                    matched_label = label_hash[rgx.pattern]
            return matched_label, closest_match

        label_rgxs, label_hash = self.label_rgxs
        closest_match = 0 if target == "END" else end
        matched_label = None
        search_start = start
        if target == "END" and end - start > 50:  # limit how far back to look
            search_start = end - 50
        for rgx in label_rgxs:
            match = rgx.finditer(line, search_start, end)
            matched_label, closest_match = check_match(match, closest_match, matched_label)
        if matched_label:
            return LabelMatch(matched_label, True)

        if search_start != start:  # check for non-priority matches
            for rgx in label_rgxs:
                match = rgx.finditer(line, start, end)
                matched_label, closest_match = check_match(match, closest_match, matched_label)
        if matched_label:
            return LabelMatch(matched_label, False)
        return None

    def valid_range(self, year: int, month: int, day: int | None = None) -> bool:
        lookahead_year = datetime.now(tz=timezone.utc).year + 5
        return (
            (month >= 1 and month <= 12)
            and (year > 1980 and year <= lookahead_year)
            and (not day or (day >= 1 and day <= 31))
        )

    def is_best_effective(self, test_date: DateMatch, existing_date: DateMatch | None) -> bool:
        if test_date.date == self.end_date.date:
            return False
        elif existing_date is None:
            return True
        today = datetime.now()
        existing_delta = abs(today - existing_date.date)
        new_delta = abs(today - test_date.date)
        if new_delta < existing_delta:
            return True
        return False

    def pick_valid_parts(self, datetext: str):
        if len(datetext) == 6:
            # assuming we have no `day part` and mmYYYY
            maybe_month = int(datetext[:2])
            maybe_year = int(datetext[2:])
            if self.valid_range(month=maybe_month, year=maybe_year):
                return f"{maybe_year}-{maybe_month}-01"

            # assuming we have no `day part` and YYYYmm
            maybe_month = int(datetext[4:])
            maybe_year = int(datetext[:4])
            if self.valid_range(month=maybe_month, year=maybe_year):
                return f"{maybe_year}-{maybe_month}-01"

            # assuming we have no `day part` and mmddYY
            maybe_month = int(datetext[:2])
            maybe_day = int(datetext[2:4])
            maybe_year = int(datetext[4:]) + 2000
            if self.valid_range(month=maybe_month, year=maybe_year, day=maybe_day):
                return f"{maybe_year}-{maybe_month}-{maybe_day}"

        elif len(datetext) == 8:
            # assuming we have no `day part` and mmddYYYY
            maybe_month = int(datetext[:2])
            maybe_day = int(datetext[2:4])
            maybe_year = int(datetext[4:])
            if self.valid_range(month=maybe_month, year=maybe_year, day=maybe_day):
                return f"{maybe_year}-{maybe_month}-{maybe_day}"

            # assuming we have no `day part` and YYYYmmdd
            maybe_month = int(datetext[2:])
            maybe_day = int(datetext[2:4])
            maybe_year = int(datetext[:4])
            if self.valid_range(month=maybe_month, year=maybe_year, day=maybe_day):
                return f"{maybe_year}-{maybe_month}-{maybe_day}"

        elif len(datetext) == 4:
            # assuming YYYY
            maybe_year = int(datetext)
            maybe_month = 1
            maybe_day = 1
            if self.valid_range(month=maybe_month, year=maybe_year, day=maybe_day):
                return f"{maybe_year}-{maybe_month}-{maybe_day}"

        # if all else fails not a date and we skip
        raise Exception("Invalid date range")

    def check_context_chars(self, text: str, rgx: str, match: re.Match):
        search_start = 0 if match.start() < 6 else match.start() - 6
        leading_text = text[search_start : match.start()]  # noqa: E203
        leading_search = re.search(rgx, leading_text)
        if leading_search:
            return True
        search_end = match.end() + 6
        trailing_text = text[match.end() : search_end]  # noqa: E203
        trailing_search = re.search(rgx, trailing_text)
        if trailing_search:
            return True
        return False

    def get_dates(
        self, text: str, rgx_excludes: list[int] = []
    ) -> Generator[DateMatch, None, None]:
        match_count = 0
        secondary_match: DateMatch | None = None
        for i, rgx in enumerate(self.date_rgxs):
            if i in rgx_excludes:
                continue
            match = rgx.finditer(text)
            last_index = 0
            for m in match:
                try:
                    datetext = m.group()
                    if i == 0:
                        year, month = datetext[:4], datetext[4:7]
                        datetext = f"{year}-{month}-01"
                    if i >= 1 and i <= 3:
                        datetext = self.pick_valid_parts(datetext)
                    if i + 1 == len(self.date_rgxs):
                        month, year = re.split(r"[/\-|\.]", datetext)
                        datetext = f"{year}-{month}-01"
                    if i + 2 == len(self.date_rgxs):
                        if self.check_context_chars(text, r"\s*([\$\%]|mg|ml|oz)", m):
                            continue
                        month, year = re.split(r"[/\-|\.]", datetext)
                        datetext = f"20{year}-{month}-01"
                    if i + 3 == len(self.date_rgxs) or i + 4 == len(self.date_rgxs):
                        pieces = re.split(r"[., ]", datetext)
                        datetext = f"{pieces[-1]}-{pieces[0]}-01"
                    if i + 5 == len(self.date_rgxs) or i + 6 == len(self.date_rgxs):
                        # check for a following date with a year
                        second_date = self.extract_date_span(text, m.end())
                        if second_date:
                            datetext = f"{datetext} {second_date.date.year}"
                        else:
                            continue
                    datetext = datetext.replace("|", "-")
                    date = parser.parse(datetext, ignoretz=True)
                    if self.valid_range(month=date.month, year=date.year, day=date.day):
                        dm = DateMatch(date, m, last_index, rgx=i)
                        match_count += 1
                        if i == 1:
                            secondary_match = dm
                        else:
                            yield dm
                    last_index = m.end()
                except Exception as ex:
                    logging.debug(ex)
                    continue
        if match_count == 1 and secondary_match:
            # only yield these if no other matches
            yield secondary_match

    def extract_date_span(self, text: str, start: int) -> DateMatch | None:
        """
        Return date found in text if date is preceded by dash
        and no other nonwhitespace character.
        """
        separator_match = self.hyphen_rgx.search(text, start)
        if separator_match:
            dash_index = separator_match.start()
            if self.whitespace_rgx.search(text, start, dash_index):
                return None
            closest_match: DateMatch | None = None
            for m in self.get_dates(text[dash_index:]):
                if not closest_match or m.start < closest_match.start:
                    closest_match = m
            if closest_match:
                second_date = dash_index + closest_match.start
                if not self.whitespace_rgx.search(text, dash_index + 1, second_date):
                    return closest_match
        return None

    def update_label(self, match: DateMatch, label: LabelMatch) -> None:
        """
        Check existing date label for previous best match.
        """

        future_dates = ["end_date", "next_review_date", "next_update_date"]
        now = datetime.now(tz=timezone.utc)
        if (
            label.text not in future_dates
            and label.text != "effective_date"
            and match.date.timestamp() > now.timestamp()
        ):
            return

        match.label = label
        existing_match: DateMatch = getattr(self, label.text)
        if existing_match.label:
            # default to priority label, compare dates if same priority
            if existing_match.label.priority and not label.priority:
                return
            elif not existing_match.label.priority and label.priority:
                setattr(self, label.text, match)

        # not set, set it
        if not existing_match.date:
            setattr(self, label.text, match)

        # future date take closest to today
        elif label.text in future_dates and match.date < existing_match.date:
            setattr(self, label.text, match)

        # effective date get closest to present
        elif label.text == "effective_date" and self.is_best_effective(match, existing_match):
            setattr(self, label.text, match)

        # past date take closest to today
        elif match.date > existing_match.date and match.date.timestamp() < now.timestamp():
            setattr(self, label.text, match)

    def is_references_header(self, line: str) -> bool:
        search = "references"
        if search in line and not any(c.isalpha() for c in line.replace(search, "")):
            return True
        return False

    def extract_dates(self, text: str, label_texts: list[str] = []) -> None:
        """
        Extract dates and labels from provided text.
        Set label attributes to extracted dates.
        """

        prev_line = ""
        prev_line_index = 0
        prev_label: LabelMatch | None = None
        ends_with_comma = False
        word_count = 0
        for line in text.split("\n"):
            if self.is_references_header(line.lower()):
                break
            if self.exclude_text(line):
                prev_line = ""
                prev_line_index = 0
                continue
            if qrt_date := self.check_quarter_text(line):
                self.heading_dates.append(qrt_date)
                self.unclassified_dates.add(qrt_date.date)
            if ends_with_comma:  # append previous line to current line to restore context
                line = f"{prev_line} {line}"
            latest_match = 0  # Latest date match on current line
            label: LabelMatch | None = None
            for m in self.get_dates(line):
                if m.rgx == 1 and word_count >= 20:  # only accept yyyy in heading
                    continue
                if end_date := self.extract_date_span(line, m.end):
                    self.update_label(end_date, LabelMatch("end_date", True))
                    self.update_label(m, LabelMatch("effective_date", True))
                else:
                    m.check_date_list(line)
                    label = self.get_date_label(line, m.last_date_index, m.start)
                    if not label:  # If no match, check right of date
                        label = self.get_date_label(line, m.end, m.end + 20, "START")
                    if not label:  # If no match, check previous line
                        label = self.get_date_label(prev_line, prev_line_index, len(prev_line))
                    if (
                        ends_with_comma and not label
                    ):  # if no match and previous line ends with comma, check label from the start
                        label = self.get_date_label(line, 0, m.last_date_index, "START")
                    if label:
                        # custom logic for saving labels in adjacent cells ahca.myflorida.com
                        prev_label = label if prev_line and prev_line[-1] == ":" else None
                        self.update_label(m, label)
                    elif prev_label:
                        self.update_label(m, prev_label)
                    elif word_count < 20:
                        self.heading_dates.append(m)
                self.unclassified_dates.add(m.date)
                latest_match = m.end if m.end > latest_match else latest_match
            if not label and prev_label:
                prev_label = None
            if line != "":
                ends_with_comma = True if line[-1] == "," else False
                prev_line = line
                prev_line_index = latest_match
            word_count += len(line.split(" "))

        self.check_effective_date(label_texts)
