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
        text: str,
        date_rgxs: list[re.Pattern[str]],
        label_rgxs: tuple[list[re.Pattern[str]], dict[str, str]],
    ) -> None:
        self.text = text
        self.date_rgxs = date_rgxs
        self.label_rgxs = label_rgxs
        self.whitespace_rgx = re.compile(r"\S")
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

    def get_dates(self, text: str) -> Generator[DateMatch, None, None]:
        for i, rgx in enumerate(self.date_rgxs):
            match = rgx.finditer(text)
            last_index = 0
            for m in match:
                try:
                    datetext = m.group()
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
        dash = text.find("-", start)
        if dash != -1 and not self.whitespace_rgx.search(text, start, dash):
            closest_match: DateMatch = None
            for m in self.get_dates(text[dash:]):
                if not closest_match or m.start < closest_match.start:
                    closest_match = m
            if closest_match:
                second_date = dash + closest_match.start
                if not self.whitespace_rgx.search(text, dash + 1, second_date):
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

    def extract_dates(self) -> None:
        """
        Extract dates and labels from provided text.
        Set label attributes to extracted dates.
        """

        prev_line = ""
        prev_line_index = 0
        for line in self.text.split("\n"):
            latest_match = 0  # Latest date match on current line
            if self.exclude_text(line):
                prev_line = ""
                prev_line_index = 0
                continue
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
                    if label:
                        self.update_label(m, label)
                self.unclassified_dates.add(m.date)
                latest_match = m.end if m.end > latest_match else latest_match
            if line != "":
                prev_line = line
                prev_line_index = latest_match

        self.check_effective_date()
