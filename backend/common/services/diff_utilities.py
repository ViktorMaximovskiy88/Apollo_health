import re
from dataclasses import dataclass

from diff_match_patch import diff_match_patch


@dataclass
class DiffSection:
    spans: list[tuple[int, int]]
    remove: bool = False


class Dmp(diff_match_patch):
    def diff_wordsToChars(self, text1, text2):
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

        def diff_wordsToCharsMunge(text: str):
            chars = []
            wordStart = 0
            wordEnd = -1
            while wordEnd < len(text) - 1:
                word_match = re.search(r"\s", text[wordStart:])
                if word_match:
                    wordEnd = word_match.start() + wordStart
                else:
                    wordEnd = len(text) - 1
                word = text[wordStart : wordEnd + 1]  # noqa
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

    def find_repeat_lines(self, diffs: list[tuple[int, str]]):
        """
        Parse diffs to find repeat changes throughout a file.
        Return DiffSections for inserts and deletes.
        """

        deletes: dict[str, DiffSection] = {}
        inserts: dict[str, DiffSection] = {}

        a_char_count = 0  # Number of characters into the a_text string.
        b_char_count = 0  # Number of characters into the b_text string.
        for diff in diffs:
            diff_type, diff_text = diff
            a_diff_end = a_char_count + len(diff_text)
            b_diff_end = b_char_count + len(diff_text)
            if diff_type == self.DIFF_INSERT:
                if diff_text in inserts:
                    inserts[diff_text].remove = True
                    inserts[diff_text].spans.append((b_char_count, b_diff_end))
                else:
                    line_diff = DiffSection(spans=[(b_char_count, b_diff_end)])
                    inserts[diff_text] = line_diff
            elif diff_type == self.DIFF_DELETE:
                if diff_text in deletes:
                    deletes[diff_text].remove = True
                    deletes[diff_text].spans.append((a_char_count, a_diff_end))
                else:
                    line_diff = DiffSection(spans=[(a_char_count, a_diff_end)])
                    deletes[diff_text] = line_diff
            # Update the current character count.
            if diff_type != self.DIFF_INSERT:
                a_char_count += len(diff_text)
            if diff_type != self.DIFF_DELETE:
                b_char_count += len(diff_text)

        final_deletes = [deletes[key] for key in deletes]
        final_inserts = [inserts[key] for key in inserts]

        return final_deletes, final_inserts

    def remove_diffs(
        self, deletes: list[DiffSection], inserts: list[DiffSection], a_text: str, b_text: str
    ):
        """
        Remove sections from a_text and b_text according to provided DiffSections.
        """
        if not deletes and not inserts:
            return a_text, b_text

        clean_a: list[str] = list(a_text)
        clean_b: list[str] = list(b_text)
        for section in deletes:
            if not section.remove:
                continue
            for span in section.spans:
                for i in range(span[0], span[1]):
                    clean_a[i] = " "

        for section in inserts:
            if not section.remove:
                continue
            for span in section.spans:
                for i in range(span[0], span[1]):
                    clean_b[i] = " "

        return "".join(clean_a), "".join(clean_b)
