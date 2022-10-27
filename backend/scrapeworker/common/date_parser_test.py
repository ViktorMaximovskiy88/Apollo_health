from datetime import datetime

from backend.scrapeworker.common.date_parser import DateParser
from backend.scrapeworker.common.utils import date_rgxs, label_rgxs


def test_get_date_and_label():
    text = "This contains one date, updated 2/9/2022"
    parser = DateParser(date_rgxs, label_rgxs)
    parser.extract_dates(text)
    assert len(parser.unclassified_dates) == 1
    assert parser.last_updated_date.date == datetime(2022, 2, 9)
    assert parser.effective_date.date == datetime(2022, 2, 9)

    text = """
        Multiple Formats, left and right, 05/30 expire, Published 02/21,
        updated 10/9/11, next review March 8, 2036, next update 10 January 2038 \n
        Last Review 6.30.22.
    """
    parser = DateParser(date_rgxs, label_rgxs)
    parser.extract_dates(text)
    assert len(parser.unclassified_dates) == 6
    assert parser.end_date.date == datetime(2030, 5, 1)
    assert parser.published_date.date == datetime(2021, 2, 1)
    assert parser.last_updated_date.date == datetime(2011, 10, 9)
    assert parser.last_reviewed_date.date == datetime(2022, 6, 30)
    assert parser.next_review_date.date == datetime(2036, 3, 8)
    assert parser.next_update_date.date == datetime(2038, 1, 10)

    text = """
        Different formats, rev. 1/10/20 and v. 12/12 4/20\n
        with no label match here harv.2/27/2021 \n
        and more labels - reviewed as of 03/2020 through Dec 2030
    """
    parser = DateParser(date_rgxs, label_rgxs)
    parser.extract_dates(text)
    assert len(parser.unclassified_dates) == 6
    assert parser.published_date.date == datetime(2012, 12, 1)
    assert parser.last_updated_date.date == datetime(2020, 1, 10)
    assert parser.last_reviewed_date.date == datetime(2020, 3, 1)
    assert parser.end_date.date == datetime(2030, 12, 1)


def test_all_date_formats():
    text = """
        2020-01-20 2020/02/20 2020.03.20
        04-20-2020 05/20/2020 06.20.2020
        07-20-20 08/20/20 09.20.20
        Oct 20 2020 Nov. 20 2020 Dec 20, 2020
    """
    parser = DateParser(date_rgxs, label_rgxs)
    parser.extract_dates(text)
    dates = []
    for m in range(1, 13):
        dates.append(datetime(2020, m, 20))

    assert len(parser.unclassified_dates) == 12
    for date in dates:
        assert date in parser.unclassified_dates

    text = """
        20 Jan 2021 20 Feb 2021 20 Mar. 2021
        20 April 2021 20 May, 2021 20 June 2021
        July 20, 2021 August 20 2021 September 20, 2021
    """
    parser = DateParser(date_rgxs, label_rgxs)
    parser.extract_dates(text)
    dates = []
    for m in range(1, 10):
        dates.append(datetime(2021, m, 20))

    assert len(parser.unclassified_dates) == 9
    for date in dates:
        assert date in parser.unclassified_dates

    text = """
        01/2022 02-2022 3-2022
        Apr, 2022 - May 2022. Jun. 2022
        07/22 08-22 9/22
        October, 2022. November 2022, December 2022
    """
    parser = DateParser(date_rgxs, label_rgxs)
    parser.extract_dates(text)
    dates = []
    for m in range(1, 13):
        dates.append(datetime(2022, m, 1))

    assert len(parser.unclassified_dates) == 12
    for date in dates:
        assert date in parser.unclassified_dates

    text = """
        2023|01|01 02|01|2023
        03|23 04|2023 05.23
        06.2023
    """
    parser = DateParser(date_rgxs, label_rgxs)
    parser.extract_dates(text)
    dates = []
    for m in range(1, 7):
        dates.append(datetime(2023, m, 1))

    assert len(parser.unclassified_dates) == 6
    for date in dates:
        assert date in parser.unclassified_dates


def test_get_date_and_label_multiple_lines():
    text = "The below date is the published date. \n date: 1/2/22"
    parser = DateParser(date_rgxs, label_rgxs)
    parser.extract_dates(text)
    assert parser.published_date.date == datetime(2022, 1, 2)
    assert parser.effective_date.date == datetime(2022, 1, 2)

    text = "This date is the published date: 1/2/22 \n different date: 12/11/1989"
    new_parser = DateParser(date_rgxs, label_rgxs)
    new_parser.extract_dates(text)
    assert new_parser.published_date.date == datetime(2022, 1, 2)
    assert new_parser.effective_date.date == datetime(2022, 1, 2)

    text = """
        This text has many lines with dates: 12/15/2024 \n
        There are also some blank lines. The below date is the end date.\n\n
        end Date: 12/11/2032\n
        The publish date: 02/21 \n
        10|20|2020 recent review, annual review 11|2033
    """

    many_line_parser = DateParser(date_rgxs, label_rgxs)
    many_line_parser.extract_dates(text)
    assert len(many_line_parser.unclassified_dates) == 5
    assert many_line_parser.end_date.date == datetime(2032, 12, 11)
    assert many_line_parser.published_date.date == datetime(2021, 2, 1)
    assert many_line_parser.last_reviewed_date.date == datetime(2020, 10, 20)
    assert many_line_parser.next_review_date.date == datetime(2033, 11, 1)


def test_get_label_to_the_right():
    text = "2/15/22: published \n 3/20/20"
    parser = DateParser(date_rgxs, label_rgxs)
    parser.extract_dates(text)
    assert len(parser.unclassified_dates) == 2
    assert parser.published_date.date == datetime(2022, 2, 15)
    assert parser.effective_date.date == datetime(2022, 2, 15)
    text = "2/15/22: this label is too far published"
    parser = DateParser(date_rgxs, label_rgxs)
    parser.extract_dates(text)
    assert len(parser.unclassified_dates) == 1
    assert parser.published_date.date is None
    assert parser.effective_date.date == datetime(2022, 2, 15)


def test_get_no_dates():
    text = "These lines contains no dates. \n not this one either."
    parser = DateParser(date_rgxs, label_rgxs)
    parser.extract_dates(text)
    assert parser.effective_date.date is None
    assert parser.end_date.date is None
    assert parser.last_updated_date.date is None
    assert parser.next_review_date.date is None
    assert parser.next_update_date.date is None
    assert parser.published_date.date is None
    assert len(parser.unclassified_dates) == 0


def test_select_best_match():
    text = """
        This could be the last updated date right here 12/11/1988
        \n but there's a better updated date 8/15/2020
    """
    parser = DateParser(date_rgxs, label_rgxs)
    parser.extract_dates(text)
    assert parser.last_updated_date.date == datetime(2020, 8, 15)
    assert len(parser.unclassified_dates) == 2

    text = """
        This line has multiple dates including end date 4/30/2031,
        eff. date 2021/10/31, and a better expire date 4-30-2030
    """
    parser = DateParser(date_rgxs, label_rgxs)
    parser.extract_dates(text)

    assert len(parser.unclassified_dates) == 3
    assert parser.end_date.date == datetime(2030, 4, 30)
    assert parser.effective_date.date == datetime(2021, 10, 31)


def test_extract_date_span():
    text = "12/1/2020 - 10/15/30"
    parser = DateParser(date_rgxs, label_rgxs)
    parser.extract_dates(text)
    assert len(parser.unclassified_dates) == 2
    assert parser.effective_date.date == datetime(2020, 12, 1)
    assert parser.end_date.date == datetime(2030, 10, 15)

    text = "This will also get a date May 2021     -      July 2030 with text around"
    parser = DateParser(date_rgxs, label_rgxs)
    parser.extract_dates(text)
    assert len(parser.unclassified_dates) == 2
    assert parser.effective_date.date == datetime(2021, 5, 1)
    assert parser.end_date.date == datetime(2030, 7, 1)

    text = "This will not grab a date span 10-10-2021 because - July 2030 of the text left of dash"
    parser = DateParser(date_rgxs, label_rgxs)
    parser.extract_dates(text)
    assert len(parser.unclassified_dates) == 2
    assert parser.effective_date.date == datetime(2021, 10, 10)
    assert parser.end_date.date is None

    text = "This will not grab a date span 12-10-2021 - because July 2030 of the text right of dash"
    parser = DateParser(date_rgxs, label_rgxs)
    parser.extract_dates(text)
    assert len(parser.unclassified_dates) == 2
    assert parser.effective_date.date == datetime(2021, 12, 10)
    assert parser.end_date.date is None

    text = """
        date span 12/10/2021-1/5/2031 and
        other dates published 2010-10-31
    """
    parser = DateParser(date_rgxs, label_rgxs)
    parser.extract_dates(text)
    assert len(parser.unclassified_dates) == 3
    assert parser.effective_date.date == datetime(2021, 12, 10)
    assert parser.end_date.date == datetime(2031, 1, 5)
    assert parser.published_date.date == datetime(2010, 10, 31)

    text = "date span with only 1 year and unicode separator January 1 – December 31, 2022"
    parser = DateParser(date_rgxs, label_rgxs)
    parser.extract_dates(text)
    assert len(parser.unclassified_dates) == 2
    assert parser.effective_date.date == datetime(2022, 1, 1)
    assert parser.end_date.date == datetime(2022, 12, 31)


def test_exclusions():
    text = "this line is exluded OMB Approval 3/15/22 \n this one isn't 11|20|21"
    parser = DateParser(date_rgxs, label_rgxs)
    parser.extract_dates(text)
    assert len(parser.unclassified_dates) == 1
    assert parser.effective_date.date == datetime(2021, 11, 20)


def test_exclude_references():
    text = """
        4. References \n
        date span 12/10/2021-1/5/2031
    """
    parser = DateParser(date_rgxs, label_rgxs)
    parser.extract_dates(text)
    assert len(parser.unclassified_dates) == 0


def test_default_effective_date():
    text = "Contains two dates with no labels, 2/9/2022, May 5 2020"
    parser = DateParser(date_rgxs, label_rgxs)
    parser.extract_dates(text)
    assert len(parser.unclassified_dates) == 2
    assert parser.effective_date.date == datetime(2022, 2, 9)

    text = "Contains two dates with updated date override, updated 2/9/2022, effective May 5 2020"
    parser = DateParser(date_rgxs, label_rgxs)
    parser.extract_dates(text)
    assert len(parser.unclassified_dates) == 2
    assert parser.last_updated_date.date == datetime(2022, 2, 9)
    assert parser.effective_date.date == datetime(2022, 2, 9)

    text = (
        "Contains two dates with published date override, published 3/9/2022, effective May 5 2020"
    )
    parser = DateParser(date_rgxs, label_rgxs)
    parser.extract_dates(text)
    assert len(parser.unclassified_dates) == 2
    assert parser.published_date.date == datetime(2022, 3, 9)
    assert parser.effective_date.date == datetime(2022, 3, 9)
