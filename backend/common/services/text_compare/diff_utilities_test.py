import os

import aiofiles
import pytest

from backend.common.services.text_compare.diff_utilities import DiffSection, Dmp, WordSpan


def test_clean_line():
    line = "Testing remove words: Updated 12/1/2022"
    dmp = Dmp()
    clean_line, words_removed = dmp._clean_line(line, 0, 0)
    assert clean_line == "Testing remove words:                  "
    assert words_removed == [
        WordSpan(page_num=0, start=3, end=4),
        WordSpan(page_num=0, start=4, end=5),
    ]


class TestPreProcessText:
    def test_preprocess_text_delta(self):
        a_line = "Testing remove words: Updated 12/1/2022\fMore words 12/2/20"
        b_line = "Testing remove words: Updated 12/1/2022\fDifferent 01.02.21 words"
        dmp = Dmp()
        a_removed, b_removed = dmp.preprocess_text_delta(a_line, b_line)
        assert a_removed == [
            WordSpan(page_num=0, start=3, end=4),
            WordSpan(page_num=0, start=4, end=5),
            WordSpan(page_num=1, start=2, end=3),
        ]
        assert b_removed == [
            WordSpan(page_num=0, start=3, end=4),
            WordSpan(page_num=0, start=4, end=5),
            WordSpan(page_num=1, start=1, end=2),
        ]

    def test_preprocess_diff(self):  # noqa
        """
        Should whiteout
            - page numbers
            - repeated identical line diffs
            - repeated lines appearing once on every page
            - dates and date keywords
        """
        dmp = Dmp(exclude_digits=True)
        a_text = "string 1\nthis is a footer\n\fstring 2\nthis is a footer\n updated 12/20/20"
        b_text = (
            "string 1\ndifferent footer here\n\fstring 2\ndifferent footer here\n updated 12/20/21"
        )
        expected_a = "string  \n                \n\fstring  \n                \n                 "
        expected_b = (
            "string  \n                     \n\fstring  \n                     \n                 "
        )
        cleaned_a, cleaned_b = dmp.preprocess_text(a_text, b_text)
        assert expected_a == cleaned_a
        assert expected_b == cleaned_b

    @pytest.mark.asyncio
    async def test_remove_footers(self):  # noqa
        current_path = os.path.dirname(os.path.realpath(__file__))
        fixture_path = os.path.join(current_path, "../__fixtures__")
        file_path = os.path.join(fixture_path, "test_text.txt")
        expected_path = os.path.join(fixture_path, "expected_test_text.txt")

        async with aiofiles.open(file_path, mode="r") as file:
            test_text = await file.read()
        dmp = Dmp()
        clean_text, _ = dmp._remove_footers(test_text)

        async with aiofiles.open(expected_path, mode="r") as file:
            expected_text = await file.read()
            assert clean_text == expected_text


class TestCreateWordDiffs:
    def test_normalize_newlines(self):
        a_line = "line 1 line 2\n"
        b_line = "line 1\nline 2\n"
        dmp = Dmp()
        diffs = dmp.create_word_diffs(a_line, b_line)
        assert diffs == [(0, "line 1 line 2 ")]


class TestGetDiffSections:
    def test_get_diff_sections(self):
        a_line = "line 1\nline 2\n"
        b_line = "line 1\nline two\n"
        dmp = Dmp()
        diffs = dmp.create_word_diffs(a_line, b_line)
        deletes, inserts = dmp.get_diff_sections(diffs)

        assert deletes == [
            DiffSection(
                char_spans=[(12, 14)],
                word_spans=[WordSpan(page_num=None, start=3, end=4)],
                diff_text="2 ",
                diff_method=-1,
                remove=False,
            )
        ]
        assert inserts == [
            DiffSection(
                char_spans=[(12, 16)],
                word_spans=[WordSpan(page_num=None, start=3, end=4)],
                diff_text="two ",
                diff_method=1,
                remove=False,
            )
        ]

    def test_get_long_sections(self):
        a_line = "line one\nline two\nline three\fnew page"
        b_line = "line 1\nline two\nline 3\fnew page here"
        dmp = Dmp()
        diffs = dmp.create_word_diffs(a_line, b_line)
        deletes, inserts = dmp.get_diff_sections(diffs)

        assert deletes == [
            DiffSection(
                char_spans=[(5, 9)],
                word_spans=[WordSpan(page_num=None, start=1, end=2)],
                diff_text="one ",
                diff_method=-1,
                remove=False,
            ),
            DiffSection(
                char_spans=[(23, 29)],
                word_spans=[WordSpan(page_num=None, start=5, end=6)],
                diff_text="three ",
                diff_method=-1,
                remove=False,
            ),
            DiffSection(
                char_spans=[(33, 37)],
                word_spans=[WordSpan(page_num=None, start=7, end=8)],
                diff_text="page",
                diff_method=-1,
                remove=False,
            ),
        ]
        assert inserts == [
            DiffSection(
                char_spans=[(5, 7)],
                word_spans=[WordSpan(page_num=None, start=1, end=2)],
                diff_text="1 ",
                diff_method=1,
                remove=False,
            ),
            DiffSection(
                char_spans=[(21, 23)],
                word_spans=[WordSpan(page_num=None, start=5, end=6)],
                diff_text="3 ",
                diff_method=1,
                remove=False,
            ),
            DiffSection(
                char_spans=[(27, 36)],
                word_spans=[WordSpan(page_num=None, start=7, end=9)],
                diff_text="page here",
                diff_method=1,
                remove=False,
            ),
        ]
