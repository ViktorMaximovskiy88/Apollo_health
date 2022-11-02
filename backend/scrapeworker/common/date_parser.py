import logging
import re
from datetime import datetime, timezone
from typing import Generator

from dateutil import parser


class DateMatch:
    def __init__(
        self,
        date: datetime | None = None,
        match: re.Match[str] = None,
        last_date_index: int = None,
    ) -> None:
        self.date = date
        self.last_date_index = last_date_index
        if match:
            self.start: int = match.start()
            self.end: int = match.end()
        else:
            self.start: int = None
            self.end: int = None


class DateParser:
    def __init__(
        self,
        date_rgxs: list[re.Pattern[str]],
        label_rgxs: tuple[list[re.Pattern[str]], dict[str, str]],
    ) -> None:
        self.date_rgxs = date_rgxs
        self.label_rgxs = label_rgxs
        self.whitespace_rgx = re.compile(r"\S")
        self.hyphen_rgx = re.compile(r"[\u2010-\u2015]|-")  # unicode hyphens
        self.effective_date = DateMatch()
        self.end_date = DateMatch()
        self.last_updated_date = DateMatch()
        self.last_reviewed_date = DateMatch()
        self.next_review_date = DateMatch()
        self.next_update_date = DateMatch()
        self.published_date = DateMatch()
        self.unclassified_dates: set[datetime] = set()

    def exclude_text(self, text: str) -> bool:
        exclusions = ["omb approval"]
        lower_text = text.lower()
        for exclusion in exclusions:
            if exclusion in lower_text:
                return True
        return False

    def get_date_label(self, line: str, start: int, end: int, target="END") -> str | None:
        """
        Find date label between start and end indexes of given string.
        If multiple labels found, returns the label found closest to the `target` index.
        """

        label_rgxs, label_hash = self.label_rgxs

        closest_match = 0 if target == "END" else end
        matched_label = None
        if target == "END" and end - start > 120:  # limit how far back to look
            start = end - 120
        for rgx in label_rgxs:
            match = rgx.finditer(line, start, end)
            for m in match:
                if target == "END" and m.end() >= closest_match:
                    closest_match = m.end()
                    matched_label = label_hash[rgx.pattern]
                elif target == "START" and m.start() <= closest_match:
                    closest_match = m.start()
                    matched_label = label_hash[rgx.pattern]

        return matched_label

    def valid_range(self, year: int, month: int, day: int | None) -> bool:
        lookahead_year = datetime.now(tz=timezone.utc).year + 5
        return (
            (month >= 1 and month <= 12)
            and (year > 1980 and year < lookahead_year)
            and (not day or (day >= 1 and day <= 31))
        )

    def pick_valid_parts(self, datetext: str):
        if len(datetext) == 6:
            # assuming we have no `day part` and mmYYYY
            maybe_month = int(datetext[:2])
            maybe_year = int(datetext[4:])
            if self.valid_range(month=maybe_month, year=maybe_year):
                return f"{maybe_year}-{maybe_month}-01"

            # assuming we have no `day part` and YYYYmm
            maybe_month = int(datetext[2:])
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

        # if all else fails not a date and we skip
        raise Exception("Invalid date range")

    def get_dates(self, text: str) -> Generator[DateMatch, None, None]:
        for i, rgx in enumerate(self.date_rgxs):
            match = rgx.finditer(text)
            last_index = 0
            for m in match:
                try:
                    datetext = m.group()
                    if i == 0:
                        datetext = self.pick_valid_parts(datetext)
                    if i + 1 == len(self.date_rgxs):
                        month, year = re.split(r"[/\-|\.]", datetext)
                        datetext = f"{year}-{month}-01"
                    if i + 2 == len(self.date_rgxs):
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
                    yield DateMatch(date, m, last_index)
                    last_index = m.end()
                except Exception as ex:
                    logging.debug(ex)
                    continue

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
            closest_match: DateMatch = None
            for m in self.get_dates(text[dash_index:]):
                if not closest_match or m.start < closest_match.start:
                    closest_match = m
            if closest_match:
                second_date = dash_index + closest_match.start
                if not self.whitespace_rgx.search(text, dash_index + 1, second_date):
                    return closest_match
        return None

    def check_effective_date(self):
        def valid_eff(date: datetime) -> bool:
            return date != self.next_review_date.date

        max_labeled_date: DateMatch | None = None
        if self.published_date.date and valid_eff(self.published_date.date):
            max_labeled_date = self.published_date
        if self.last_updated_date.date and valid_eff(self.last_updated_date.date):
            if not max_labeled_date or self.last_updated_date.date > max_labeled_date.date:
                max_labeled_date = self.last_updated_date

        if self.effective_date.date:
            if max_labeled_date and self.effective_date.date < max_labeled_date.date:
                self.effective_date = max_labeled_date
        else:
            if max_labeled_date:
                self.effective_date = max_labeled_date
            else:
                now = datetime.now(tz=timezone.utc)
                dates_in_the_past = list(
                    filter(lambda d: now.timestamp() > d.timestamp(), self.unclassified_dates)
                )
                if dates_in_the_past:
                    latest_date = max(dates_in_the_past)
                    if valid_eff(latest_date):
                        self.effective_date = DateMatch(latest_date)

    def update_label(
        self,
        match: DateMatch,
        label: str,
    ) -> None:
        """
        Check existing date label for previous best match.
        Set label to new date if current match is closer to today's date.
        """

        future_dates = ["end_date", "next_review_date", "next_update_date"]
        now = datetime.now(tz=timezone.utc)
        existing_label: DateMatch = getattr(self, label)
        if label in future_dates:
            if not existing_label.date or existing_label.date > match.date:
                setattr(self, label, match)
        else:
            if now.timestamp() < match.date.timestamp():
                return
            elif not existing_label.date or existing_label.date < match.date:
                setattr(self, label, match)
        return

    def is_references_header(self, line: str) -> bool:
        search = "references"
        if search in line and not any(c.isalpha() for c in line.replace(search, "")):
            return True

    def extract_dates(self, text: str) -> None:
        """
        Extract dates and labels from provided text.
        Set label attributes to extracted dates.
        """

        prev_line = ""
        prev_line_index = 0
        prev_label = ""
        ends_with_comma = False
        for line in text.split("\n"):
            if self.is_references_header(line.lower()):
                break
            latest_match = 0  # Latest date match on current line
            if self.exclude_text(line):
                prev_line = ""
                prev_line_index = 0
                continue
            if ends_with_comma:  # append previous line to current line to restore context
                line = f"{prev_line} {line}"
            for m in self.get_dates(line):
                end_date = self.extract_date_span(line, m.end)
                if end_date:
                    self.update_label(m, "effective_date")
                    self.update_label(end_date, "end_date")
                else:
                    label = self.get_date_label(line, m.last_date_index, m.start)
                    if not label:  # If no match, check right of date
                        label = self.get_date_label(line, m.end, m.end + 20, "START")
                    if not label:  # If no match, check previous line
                        label = self.get_date_label(prev_line, prev_line_index, len(prev_line))
                    if (
                        ends_with_comma and not label
                    ):  # if no match and previous line ends with comma, check label from the start
                        label = self.get_date_label(line, 0, m.last_date_index, "START")
                    if not label and prev_label:
                        self.update_label(m, prev_label)
                    if label:
                        # custom logic for saving labels in adjacent cells ahca.myflorida.com
                        prev_label = label if prev_line and prev_line[-1] == ":" else None
                        self.update_label(m, label)
                self.unclassified_dates.add(m.date)
                latest_match = m.end if m.end > latest_match else latest_match
            if line != "":
                ends_with_comma = True if line[-1] == "," else False
                prev_line = line
                prev_line_index = latest_match

        self.check_effective_date()
