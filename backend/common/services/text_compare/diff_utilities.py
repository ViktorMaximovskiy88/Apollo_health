import re
from dataclasses import dataclass

from diff_match_patch import diff_match_patch

from backend.scrapeworker.common.date_parser import DateParser
from backend.scrapeworker.common.utils import date_rgxs, digit_rgx, label_rgxs


@dataclass
class LineInfo:
    line_num: int
    word_span: tuple[int, int]


@dataclass
class WordSpan:
    """
    Start and end word numbers in document. Can be page offset aware or naive
    """

    page_num: int | None
    start: int
    end: int


@dataclass
class DiffSection:
    char_spans: list[tuple[int, int]]
    word_spans: list[WordSpan]
    diff_text: str
    diff_method: int
    remove: bool = False


class Dmp(diff_match_patch):
    """
    Extends diff_match_patch library.
    Provides additional methods for cleaning text to reduce diff noise
    and for working with diff_match_patch returns
    """

    SPECIAL_CHARS = re.compile(r"[^\w%<>= ]")  # any non-word char, except %<>=

    def __init__(self, exclude_digits: bool = False, *args, **kwargs):
        super(Dmp, self).__init__(*args, **kwargs)
        self.exclude_digits = exclude_digits

    def _remove_repeat_lines(self, a_text, b_text):
        lines = self.diff_linesToChars(a_text, b_text)
        diffs = self.diff_main(lines[0], lines[1], False)
        self.diff_charsToLines(diffs, lines[2])
        deletes, inserts = self.get_diff_sections(diffs)
        return self.remove_diffs(deletes, inserts, a_text, b_text)

    def _has_remove_text(self, text: str) -> bool:
        strp_text = text.strip()
        date_parser = DateParser(date_rgxs, label_rgxs)
        dates = date_parser.get_dates(strp_text)
        match = next(dates, None)
        if not match and self.exclude_digits:
            match = re.match(digit_rgx, strp_text)
        if not match:
            match = re.fullmatch(self.SPECIAL_CHARS, strp_text)
        if not match:
            for rgx in label_rgxs[0]:
                match = re.match(rgx, strp_text)
                if match:
                    break
        return bool(match)

    def _clean_line(self, line: str, page_num: int, word_count: int):
        cleaned_line = []
        words = line.split(" ")
        words_removed: list[WordSpan] = []
        for i, word in enumerate(words):
            cleaned_word = word
            if self._has_remove_text(word):
                cleaned_word = "".join([" " for _ in word])
                word_span = WordSpan(
                    page_num=page_num, start=word_count + i, end=word_count + i + 1
                )
                words_removed.append(word_span)
            cleaned_line.append(cleaned_word)
        return " ".join(cleaned_line), words_removed

    def _clean_pages(self, pages: list[str]):
        cleanded_text = []
        words_removed: list[WordSpan] = []
        for i, page in enumerate(pages):
            cleaned_page = []
            word_count = 0
            lines = page.split("\n")
            for line in lines:
                if line == "":
                    continue
                clean_line, word_spans = self._clean_line(line, i, word_count)
                cleaned_page.append(clean_line)
                words_removed += word_spans
                word_count += len(line.split(" "))
            cleanded_text.append("\n".join(cleaned_page))

        return cleanded_text, words_removed

    def _remove_exclude_text(self, a_text: str, b_text: str):
        a_pages = a_text.split("\f")
        b_pages = b_text.split("\f")
        cleaned_a, a_words_removed = self._clean_pages(a_pages)
        cleaned_b, b_words_removed = self._clean_pages(b_pages)

        return "\f".join(cleaned_a), "\f".join(cleaned_b), a_words_removed, b_words_removed

    def _remove_footers(self, text: str) -> tuple[str, list[WordSpan]]:
        repeat_lines: dict[str, list[LineInfo]] = {}
        exclude_lines: dict[str, bool] = {}  # non-removable lines

        pages = text.split("\f")
        page_count = len(pages)
        if page_count < 2:
            return text, []
        lines_by_page = list(map(lambda page: page.split("\n"), pages))

        def get_word_count(line: str) -> int:
            words = line.split(" ")
            return len(words)

        def parse_page(lines: list[str], is_first: bool = False):
            current_page_lines: dict[str, bool] = {}
            line_word_start = 0
            line_word_end = 0
            for line_num, line in enumerate(lines):
                if not line:
                    continue
                line_word_count = get_word_count(line)
                line_word_end = line_word_start + line_word_count
                line_word_idxs = (line_word_start, line_word_end)
                line_word_start = line_word_end

                if line in current_page_lines:
                    exclude_lines[line] = True
                    continue
                else:
                    current_page_lines[line] = True

                if line in repeat_lines:
                    line_info = LineInfo(line_num, line_word_idxs)
                    repeat_lines[line].append(line_info)
                elif is_first:
                    line_info = LineInfo(line_num, line_word_idxs)
                    repeat_lines[line] = [line_info]

        def remove_lines():
            removed_words: list[WordSpan] = []
            for line in repeat_lines:
                line_infos = repeat_lines[line]
                if line in exclude_lines or len(line_infos) < page_count:
                    continue
                for page_num, line_info in enumerate(line_infos):
                    line_num = line_info.line_num
                    old_line = lines_by_page[page_num][line_num]
                    lines_by_page[page_num][line_num] = "".join([" " for _ in old_line])
                    word_span = WordSpan(page_num, *line_info.word_span)
                    removed_words.append(word_span)
            return removed_words

        for i, lines in enumerate(lines_by_page):
            if i == 0:
                parse_page(lines, is_first=True)
            else:
                parse_page(lines)

        removed_words = remove_lines()

        final_pages = map(lambda page: "\n".join(page), lines_by_page)
        return "\f".join(final_pages), removed_words

    def preprocess_text(self, a_text: str, b_text: str) -> tuple[str, str]:
        cleaned_a, _ = self._remove_footers(a_text)
        cleaned_b, _ = self._remove_footers(b_text)
        cleaned_a, cleaned_b, _, _ = self._remove_repeat_lines(cleaned_a, cleaned_b)
        cleaned_a, cleaned_b, _, _ = self._remove_exclude_text(cleaned_a, cleaned_b)
        return cleaned_a, cleaned_b

    def preprocess_text_delta(
        self, a_text: str, b_text: str
    ) -> tuple[list[WordSpan], list[WordSpan]]:
        final_a_removed: list[WordSpan] = []
        final_b_removed: list[WordSpan] = []
        _, a_removed = self._remove_footers(a_text)
        _, b_removed = self._remove_footers(b_text)
        final_a_removed += a_removed
        final_b_removed += b_removed
        _, _, a_removed, b_removed = self._remove_exclude_text(a_text, b_text)
        final_a_removed += a_removed
        final_b_removed += b_removed
        return final_a_removed, final_b_removed

    def create_word_diffs(
        self, a: str, b: str, ignore_special_chars: bool = False
    ) -> list[tuple[int, str]]:
        words = self.diff_wordsToChars(a, b, ignore_special_chars)
        diffs = self.diff_main(words[0], words[1], False)
        self.diff_charsToLines(diffs, words[2])
        return diffs

    def diff_wordsToChars(self, text1, text2, ignore_special_chars: bool = False):
        # Extending diff_match_patch with method for word mode
        # https://github.com/google/diff-match-patch/wiki/Line-or-Word-Diffs#word-mode
        """Split two texts into an array of strings.  Reduce the texts to a string
        of hashes where each Unicode character represents one word.

        Args:
            text1: First string.
            text2: Second string.

        Returns:
            Three element tuple, containing the encoded text1, the encoded text2 and
            the array of unique strings.  The zeroth element of the array of unique
            strings is intentionally blank.
        """
        wordArray = []  # e.g. wordArray[4] == "Hello\n"
        wordHash = {}  # e.g. wordHash["Hello\n"] == 4

        wordArray.append("")

        def normalize_text(text: str):
            normalized_text = re.sub(r"[\n\f]", " ", text.lower())
            if ignore_special_chars and not re.fullmatch(r"\s*", normalized_text):
                no_special_chars = re.sub(self.SPECIAL_CHARS, "", normalized_text)
                if not re.fullmatch(r"\s*", no_special_chars):
                    normalized_text = no_special_chars
            return normalized_text

        def diff_wordsToCharsMunge(text: str):
            chars = []
            wordStart = 0
            wordEnd = -1
            while wordEnd < len(text) - 1:
                word_match = re.search(r"[\s\n\f]", text[wordStart:])
                if word_match:
                    wordEnd = word_match.start() + wordStart
                else:
                    wordEnd = len(text) - 1
                word = text[wordStart : wordEnd + 1]  # noqa
                word = normalize_text(word)
                # if word is only white space, skip
                if re.fullmatch(r"\s*", word):
                    pass
                elif word in wordHash:
                    chars.append(chr(wordHash[word]))
                else:
                    if len(wordArray) == maxLines:
                        word = text[wordStart:]
                        wordEnd = len(text)
                    wordArray.append(word)
                    wordHash[word] = len(wordArray) - 1
                    chars.append(chr(len(wordArray) - 1))
                wordStart = wordEnd + 1
            return "".join(chars)

        maxLines = 666666
        chars1 = diff_wordsToCharsMunge(text1)
        maxLines = 1114111
        chars2 = diff_wordsToCharsMunge(text2)
        return (chars1, chars2, wordArray)

    def exclude_diff_text(self, text: str):
        exclude_diffs = ["\n", ""]
        if text in exclude_diffs:
            return True
        return False

    def word_count_by_page(self, diff_text: str) -> list[int]:
        lengths: list[int] = []
        pages = diff_text.split("\f")
        for page in pages:
            word_count = len([word for word in re.split(r"\s", page.strip()) if word])
            lengths.append(word_count)
        return lengths

    def get_word_positions(self, word_counts: list[int], word_count: int, page_count: int | None):
        word_spans: list[WordSpan] = []
        word_end = word_count
        page_end = page_count
        for i, count in enumerate(word_counts):
            if i == 0:
                word_end = word_count + count
                word_spans.append(WordSpan(page_num=page_count, start=word_count, end=word_end))
            else:
                word_end = count
                if page_end is not None:
                    page_end += 1
                word_spans.append(WordSpan(page_num=page_end, start=0, end=count))
        return word_end, page_end, word_spans

    def get_diff_sections(self, diffs: list[tuple[int, str]], page_breaks: bool = True):
        """
        Parse diffs and return DiffSections for inserts and deletes.
        """

        deletes: dict[str, DiffSection] = {}
        inserts: dict[str, DiffSection] = {}
        a_char_count = 0  # Number of characters into the a_text string.
        b_char_count = 0  # Number of characters into the b_text string.
        a_word_count = 0  # Number of words into the a_text string.
        b_word_count = 0  # Number of words into the b_text string.
        a_page_count = 0 if page_breaks else None  # Number of pages into the a_text string.
        b_page_count = 0 if page_breaks else None  # Number of pages into the b_text string.
        for diff in diffs:
            diff_type, diff_text = diff
            if self.exclude_diff_text(diff_text):
                continue
            a_diff_end = a_char_count + len(diff_text)
            b_diff_end = b_char_count + len(diff_text)
            word_counts = self.word_count_by_page(diff_text)
            a_word_end, a_page_end, a_word_spans = self.get_word_positions(
                word_counts, a_word_count, a_page_count
            )
            b_word_end, b_page_end, b_word_spans = self.get_word_positions(
                word_counts, b_word_count, b_page_count
            )
            if diff_type == self.DIFF_INSERT:
                if diff_text in inserts:
                    inserts[diff_text].remove = True
                    inserts[diff_text].char_spans.append((b_char_count, b_diff_end))
                    inserts[diff_text].word_spans += b_word_spans
                else:
                    line_diff = DiffSection(
                        char_spans=[(b_char_count, b_diff_end)],
                        word_spans=b_word_spans,
                        diff_text=diff_text,
                        diff_method=diff_type,
                    )
                    inserts[diff_text] = line_diff
            elif diff_type == self.DIFF_DELETE:
                if diff_text in deletes:
                    deletes[diff_text].remove = True
                    deletes[diff_text].char_spans.append((a_char_count, a_diff_end))
                    deletes[diff_text].word_spans += a_word_spans
                else:
                    line_diff = DiffSection(
                        char_spans=[(a_char_count, a_diff_end)],
                        word_spans=a_word_spans,
                        diff_text=diff_text,
                        diff_method=diff_type,
                    )
                    deletes[diff_text] = line_diff
            # Update the current character count.
            if diff_type != self.DIFF_INSERT:
                a_word_count = a_word_end
                a_page_count = a_page_end
                a_char_count += len(diff_text)
            if diff_type != self.DIFF_DELETE:
                b_word_count = b_word_end
                b_page_count = b_page_end
                b_char_count += len(diff_text)

        final_deletes = [deletes[key] for key in deletes]
        final_inserts = [inserts[key] for key in inserts]

        return final_deletes, final_inserts

    def remove_diffs(
        self, deletes: list[DiffSection], inserts: list[DiffSection], a_text: str, b_text: str
    ) -> tuple[str, str, list[WordSpan], list[WordSpan]]:
        """
        Remove sections from a_text and b_text according to provided DiffSections.
        """
        a_remove_words: list[WordSpan] = []
        b_remove_words: list[WordSpan] = []
        if not deletes and not inserts:
            return a_text, b_text, a_remove_words, b_remove_words

        clean_a: list[str] = list(a_text)
        clean_b: list[str] = list(b_text)
        for section in deletes:
            if not section.remove:
                continue
            for span in section.char_spans:
                for i in range(span[0], span[1]):
                    clean_a[i] = " "
            a_remove_words += section.word_spans

        for section in inserts:
            if not section.remove:
                continue
            for span in section.char_spans:
                for i in range(span[0], span[1]):
                    clean_b[i] = " "
            b_remove_words += section.word_spans

        return "".join(clean_a), "".join(clean_b), a_remove_words, b_remove_words
