from datetime import datetime
from backend.scrapeworker.common.date_parser import DateParser
from backend.scrapeworker.common.utils import date_rgxs, label_rgxs


def test_get_date_and_label():
    text = "This contains one date, updated 2/9/2022"
    parser = DateParser(text, date_rgxs, label_rgxs)
    parser.extract_dates()
    assert len(parser.unclassified_dates) == 1
    assert parser.last_updated_date == {"date": datetime(2022, 2, 9)}
    assert parser.effective_date == {
        "date": datetime(2022, 2, 9),
    }

    text = """
        Multiple Formats, left and right, 05/30 expire, Published 02/21, updated 10/9/11, next review March 8, 2036, next update 10 January 2038 \n
        Last Review 6.30.22.
    """
    parser = DateParser(text, date_rgxs, label_rgxs)
    parser.extract_dates()
    assert len(parser.unclassified_dates) == 6
    assert parser.end_date == {"date": datetime(2030, 5, 1)}
    assert parser.published_date == {"date": datetime(2021, 2, 1)}
    assert parser.last_updated_date == {"date": datetime(2011, 10, 9)}
    assert parser.last_reviewed_date == {"date": datetime(2022, 6, 30)}
    assert parser.next_review_date == {"date": datetime(2036, 3, 8)}
    assert parser.next_update_date == {"date": datetime(2038, 1, 10)}

    text = """
        Different formats, rev. 1/10/20 and v. 12/12 \n
        with no label match here harv.2/1/2021
    """
    parser = DateParser(text, date_rgxs, label_rgxs)
    parser.extract_dates()
    assert len(parser.unclassified_dates) == 3
    assert parser.published_date == {"date": datetime(2012, 12, 1)}
    assert parser.last_updated_date == {"date": datetime(2020, 1, 10)}


def test_get_date_and_label_multiple_lines():
    text = "The below date is the published date. \n date: 1/2/22"
    parser = DateParser(text, date_rgxs, label_rgxs)
    parser.extract_dates()
    assert parser.published_date == {
        "date": datetime(2022, 1, 2),
    }
    assert parser.effective_date == {
        "date": datetime(2022, 1, 2),
    }

    text = "This date is the published date: 1/2/22 \n different date: 12/11/1989"
    new_parser = DateParser(text, date_rgxs, label_rgxs)
    new_parser.extract_dates()
    assert new_parser.published_date == {"date": datetime(2022, 1, 2)}
    assert new_parser.effective_date == {
        "date": datetime(2022, 1, 2),
    }

    text = """
        This text has many lines with dates: 12/15/2024 \n
        There are also some blank lines. The below date is the end date.\n\n
        end Date: 12/11/2032\n
        The publish date: 02/21
    """

    many_line_parser = DateParser(text, date_rgxs, label_rgxs)
    many_line_parser.extract_dates()
    assert len(many_line_parser.unclassified_dates) == 3
    assert many_line_parser.end_date == {"date": datetime(2032, 12, 11)}
    assert many_line_parser.published_date == {"date": datetime(2021, 2, 1)}


def test_get_label_to_the_right():
    text = "2/15/22: published \n 3/20/20"
    parser = DateParser(text, date_rgxs, label_rgxs)
    parser.extract_dates()
    assert len(parser.unclassified_dates) == 2
    assert parser.published_date == {
        "date": datetime(2022, 2, 15),
    }
    assert parser.effective_date == {
        "date": datetime(2022, 2, 15),
    }
    text = "2/15/22: this label is too far published"
    parser = DateParser(text, date_rgxs, label_rgxs)
    parser.extract_dates()
    assert len(parser.unclassified_dates) == 1
    assert parser.published_date == {
        "date": None,
    }
    assert parser.effective_date == {
        "date": datetime(2022, 2, 15),
    }


def test_get_no_dates():
    text = "These lines contains no dates. \n not this one either."
    parser = DateParser(text, date_rgxs, label_rgxs)
    parser.extract_dates()
    assert parser.effective_date == {
        "date": None,
    }
    assert parser.end_date == {"date": None}
    assert parser.last_updated_date == {
        "date": None,
    }
    assert parser.next_review_date == {
        "date": None,
    }
    assert parser.next_update_date == {
        "date": None,
    }
    assert parser.published_date == {
        "date": None,
    }
    assert len(parser.unclassified_dates) == 0


def test_select_best_match():
    text = "This could be the last updated date right here 12/11/1988 \n but there's a better updated date 8/15/2020"
    parser = DateParser(text, date_rgxs, label_rgxs)
    parser.extract_dates()
    assert parser.last_updated_date == {"date": datetime(2020, 8, 15)}
    assert len(parser.unclassified_dates) == 2

    text = "This line has multiple dates including end date 4/30/2031, eff. date 2021/10/31, and a better expire date 4-30-2030"
    parser = DateParser(text, date_rgxs, label_rgxs)
    parser.extract_dates()

    assert len(parser.unclassified_dates) == 3
    assert parser.end_date == {"date": datetime(2030, 4, 30)}
    assert parser.effective_date == {"date": datetime(2021, 10, 31)}
