from dateutil import parser
from datetime import datetime
from re import Pattern


class DateParser:
    def __init__(
        self,
        text: str,
        date_rgxs: list[Pattern[str]],
        label_rgxs: tuple[list[Pattern[str]], dict[str, str]],
    ) -> None:
        self.text = text
        self.date_rgxs = date_rgxs
        self.label_rgxs = label_rgxs
        self.effective_date = {
            "date": None,
        }
        self.end_date = {
            "date": None,
        }
        self.last_updated_date = {
            "date": None,
        }
        self.last_reviewed_date = {
            "date": None,
        }
        self.next_review_date = {
            "date": None,
        }
        self.next_update_date = {
            "date": None,
        }
        self.published_date = {
            "date": None,
        }
        self.unclassified_dates = set()

    def get_date_label(
        self, line: str, start: int, end: int, target="END"
    ) -> str | None:
        """
        Find date label between start and end indexes of given string.
        If multiple labels found, returns the label found closest to the `target` index.
        """

        label_rgxs, label_hash = self.label_rgxs

        closest_match = 0 if target == "END" else end
        matched_label = None
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

    def select_effective_date(self, dates: set[datetime]) -> datetime | None:
        """
        Select effective date as the highest date not in the future
        """

        now = datetime.now()
        dates_in_the_past = list(filter(lambda d: now > d, dates))
        if dates_in_the_past:
            return max(dates_in_the_past)
        else:
            return None

    def update_label(
        self,
        date: datetime,
        label: str,
    ) -> None:
        """
        Check existing date label for previous best match.
        Set label to new date if current match is closer to today's date.
        """

        future_dates = ["end_date", "next_review_date", "next_update_date"]
        now = datetime.now()
        existing_label = getattr(self, label)
        if label in future_dates:
            if now > date:
                return
            elif not existing_label["date"] or existing_label["date"] > date:
                new_label_data = {"date": date}
                setattr(self, label, new_label_data)
        else:
            if now < date:
                return

            if not existing_label["date"] or existing_label["date"] < date:
                new_label_data = {"date": date}
                setattr(self, label, new_label_data)

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
            for i, rgx in enumerate(self.date_rgxs):
                match = rgx.finditer(line)
                last_index = 0
                for m in match:
                    try:
                        datetext = m.group()
                        if i + 1 == len(self.date_rgxs):
                            month, year = datetext.split("/")
                            datetext = f"20{year}-{month}-01"
                        if i + 2 == len(self.date_rgxs):
                            pieces = datetext.split(r"[., ]")
                            datetext = f"20{pieces[-1]}-{pieces[0]}-01"
                        date = parser.parse(datetext)
                        label = self.get_date_label(line, last_index, m.start())
                        if not label:  # If no match, check right of date
                            label = self.get_date_label(
                                line, m.end(), m.end() + 12, "START"
                            )
                        if not label:  # If no match, check previous line
                            label = self.get_date_label(
                                prev_line, prev_line_index, len(prev_line)
                            )
                        if label:
                            self.update_label(date, label)

                        self.unclassified_dates.add(date)
                        last_index = m.end()
                    except:
                        continue

                latest_match = last_index if last_index > latest_match else latest_match
            if line != "":
                prev_line = line
                prev_line_index = latest_match
        if not self.effective_date["date"]:
            self.effective_date["date"] = self.select_effective_date(  # type: ignore
                self.unclassified_dates
            )
