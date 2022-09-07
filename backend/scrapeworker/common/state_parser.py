import re

from dateutil import parser

from backend.scrapeworker.common.utils import date_rgxs, label_rgxs

state_map = {
    "AK": "Alaska",
    "AL": "Alabama",
    "AR": "Arkansas",
    "AZ": "Arizona",
    "CA": "California",
    "CO": "Colorado",
    "CT": "Connecticut",
    "DC": "District of Columbia",
    "DE": "Delaware",
    "FL": "Florida",
    "GA": "Georgia",
    "HI": "Hawaii",
    "IA": "Iowa",
    "ID": "Idaho",
    "IL": "Illinois",
    "IN": "Indiana",
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
    "MA": "Massachusetts",
    "MD": "Maryland",
    "ME": "Maine",
    "MI": "Michigan",
    "MN": "Minnesota",
    "MO": "Missouri",
    "MS": "Mississippi",
    "MT": "Montana",
    "NC": "North Carolina",
    "ND": "North Dakota",
    "NE": "Nebraska",
    "NH": "New Hampshire",
    "NJ": "New Jersey",
    "NM": "New Mexico",
    "NV": "Nevada",
    "NY": "New York",
    "OH": "Ohio",
    "OK": "Oklahoma",
    "OR": "Oregon",
    "PA": "Pennsylvania",
    "RI": "Rhode Island",
    "SC": "South Carolina",
    "SD": "South Dakota",
    "TN": "Tennessee",
    "TX": "Texas",
    "UT": "Utah",
    "VA": "Virginia",
    "VT": "Vermont",
    "WA": "Washington",
    "WI": "Wisconsin",
    "WV": "West Virginia",
    "WY": "Wyoming",
}

state_abbreviations = state_map.keys()
state_names = state_map.values()

state_abbr_search = "|".join(state_abbreviations)
# any state abbr surrounded by anything but alpha
state_abbr_regex = re.compile(
    rf"(?P<state_abbr>(?<![a-z])({state_abbr_search})(?![a-z]))", flags=re.IGNORECASE
)

state_names_search = "|".join(state_names)
# any state name surrounded by whitespace or particular punctuation
state_names_regex = re.compile(
    rf"[\s.\|\-\_\\]*?(?P<state_name>({state_names_search}))[\s.\|\-\_\\]*?", flags=re.IGNORECASE
)


def guess_state_abbr(input: str | None):
    if input is None:
        return None
    match = re.search(state_abbr_regex, input)
    return match.group("state_abbr").upper() if match else None


def guess_state_name(input: str | None):
    if input is None:
        return None
    match = re.search(state_names_regex, input)
    return match.group("state_name").title() if match else None


# a pretty strict 2xxx year match with 4 digits
# anything less isnt a good signal for lineage


year_part_regex = re.compile(r"(?P<year_part>(?<![0-9])(2[0-9]{3})(?![0-9]))")


def guess_year_part(input: str | None):
    if input is None:
        return None
    match = re.search(year_part_regex, input)
    return int(match.group("year_part")) if match else None
