import tempfile
from bisect import bisect
from copy import deepcopy
from dataclasses import dataclass
from functools import cached_property

import fitz
from fitz import Document as fitzDocument
from fitz import Page as fitzPage

from backend.common.models.doc_document import DocDocument
from backend.common.models.document import RetrievedDocument
from backend.common.services.text_compare.diff_utilities import Dmp, WordSpan
from backend.common.storage.client import DocumentStorageClient


@dataclass
class Word:
    x1: float
    y1: float
    x2: float
    y2: float
    text: str
    block_no: int
    line_no: int
    word_no: int

    def coords(self):
        return (self.x1, self.y1, self.x2, self.y2)


Page = list[Word]


class CompareDoc:
    DELETE = "delete"
    INSERT = "insert"

    def __init__(self, fitz_pdf_doc: fitzDocument) -> None:
        self.fitz_pdf_doc = fitz_pdf_doc
        self.pages: list[Page] = []
        self.clean_pages: list[Page] = []
        self.clean_text: str = ""
        self.set_pages()

    def set_pages(self) -> None:
        pages = []
        for page in self.fitz_pdf_doc.pages():
            pages.append(self.create_words(page))
        self.pages = pages

    def process_page_offset(self, span: WordSpan, clean_pages: bool = False):
        span1: WordSpan | None = None
        span2: WordSpan | None = None
        offsets = self.page_word_offsets if not clean_pages else self.clean_page_word_offsets
        start_page = bisect(offsets, span.start) - 1
        end_page = bisect(offsets, span.end) - 1

        start_word = span.start - offsets[start_page]
        if start_page == end_page:
            end_word = span.end - offsets[start_page]
            span1 = WordSpan(page_num=start_page, start=start_word, end=end_word)
        else:
            page_break = offsets[end_page] - offsets[start_page]
            end_word = span.end - offsets[end_page]
            span1 = WordSpan(page_num=start_page, start=start_word, end=page_break)
            span2 = WordSpan(page_num=end_page, start=0, end=end_word)

        return span1, span2

    def set_clean_pages(self, removed_words: list[WordSpan]) -> None:
        clean_pages = deepcopy(self.pages) if not self.clean_pages else deepcopy(self.clean_pages)
        for span in removed_words:
            for word in range(span.start, span.end):
                clean_pages[span.page_num][word] = None
        for i, page in enumerate(clean_pages):
            clean_pages[i] = [word for word in page if word is not None]
        self.clean_pages = clean_pages

    def apply_word_spans(self, word_spans: list[WordSpan], method: str):
        color = {"fill": (1.0, 0.0, 0.0), "stroke": (1, 0.0, 0.0)}
        if method == self.INSERT:
            color = {"fill": (0.0, 1.0, 0.0), "stroke": (0.0, 1.0, 0.0)}
        for span in word_spans:
            page_span = span
            if page_span.page_num is None:
                span1, span2 = self.process_page_offset(span, clean_pages=True)
                page_span = span1
                if span2:
                    word_spans.append(span2)
            words = self.clean_pages[page_span.page_num][page_span.start : page_span.end]  # noqa
            for word in words:
                page = self.fitz_pdf_doc.load_page(page_span.page_num)
                annot: fitz.Annot = page.add_rect_annot(word.coords())
                annot.set_colors(colors=color)
                annot.update(opacity=0.4)

    def create_words(self, page: fitzPage) -> Page:
        words: list[tuple] = page.get_text("words")  # type: ignore
        word_objs: list[Word] = []
        for word_data in words:
            word_obj = Word(*word_data)
            word_obj.text = word_obj.text.strip()
            word_objs.append(word_obj)
        return word_objs

    def words_to_lines(self, words: list[Word]):
        lines: list[str] = []
        prev_block = 0
        prev_line = 0
        current_line: list[str] = []

        def handle_new_line(current_line: list[str]):
            lines.append(" ".join(current_line))
            new_line = []
            new_line.append(word.text)
            return new_line

        for word in words:
            if word.block_no > prev_block:
                prev_block = word.block_no
                prev_line = word.line_no
                current_line = handle_new_line(current_line)
            elif word.line_no > prev_line or word.block_no > prev_block:
                prev_line = word.line_no
                current_line = handle_new_line(current_line)
            else:
                current_line.append(word.text)
        if current_line:
            lines.append(" ".join(current_line))

        return lines

    def set_clean_text(self) -> None:
        pages: list[str] = []
        for page in self.clean_pages:
            lines = self.words_to_lines(page)
            pages.append("\n".join(lines))
        self.clean_text = "\f".join(pages)

    @cached_property
    def clean_page_word_offsets(self) -> list[int]:
        offsets: list[int] = []
        word_count = 0
        for page in self.clean_pages:
            offsets.append(word_count)
            word_count += len(page)
        return offsets

    @cached_property
    def page_word_offsets(self) -> list[int]:
        offsets: list[int] = []
        word_count = 0
        for page in self.pages:
            offsets.append(word_count)
            word_count += len(page)
        return offsets

    @cached_property
    def full_text(self) -> str:
        pages: list[str] = []
        for page in self.pages:
            lines = self.words_to_lines(page)
            pages.append("\n".join(lines))

        return "\f".join(pages)


class DocTextCompare:
    def __init__(self, doc_client: DocumentStorageClient) -> None:
        self.dmp = Dmp()
        self.doc_client = doc_client
        self.dmp.Diff_Timeout = 0  # disable timeout

    def _clean_doc_texts(self):
        removed_a, removed_b = self.dmp.preprocess_text_delta(
            self.prev_doc.full_text, self.current_doc.full_text
        )
        self.current_doc.set_clean_pages(removed_b)
        self.current_doc.set_clean_text()
        self.prev_doc.set_clean_pages(removed_a)
        self.prev_doc.set_clean_text()

    def _get_fitz_doc(self, doc: RetrievedDocument | DocDocument):
        key = f"{doc.checksum}.pdf"
        with self.doc_client.read_object_to_tempfile(key) as path:
            fitz_doc = fitz.Document(path)
        return fitz_doc

    def _set_docs(
        self, doc: RetrievedDocument | DocDocument, prev_doc: RetrievedDocument | DocDocument
    ):
        self.current_doc = CompareDoc(self._get_fitz_doc(doc))
        self.prev_doc = CompareDoc(self._get_fitz_doc(prev_doc))

    def _save_files_to_storage(
        self,
        doc: RetrievedDocument | DocDocument,
        prev_doc: RetrievedDocument | DocDocument,
        new_diff_path: str,
        prev_diff_path: str,
    ):
        base_diff_name = f"{doc.checksum}-{prev_doc.checksum}"
        prev_diff_name = f"{base_diff_name}-prev.pdf"
        new_diff_name = f"{base_diff_name}-new.pdf"
        self.doc_client.write_object(new_diff_name, new_diff_path)
        self.doc_client.write_object(prev_diff_name, prev_diff_path)

    def _save_diff_pdfs(
        self, doc: RetrievedDocument | DocDocument, prev_doc: RetrievedDocument | DocDocument
    ):
        with tempfile.NamedTemporaryFile(suffix=".pdf") as new_temp, tempfile.NamedTemporaryFile(
            suffix=".pdf"
        ) as prev_temp:
            self.current_doc.fitz_pdf_doc.save(new_temp)
            self.prev_doc.fitz_pdf_doc.save(prev_temp)

            self._save_files_to_storage(doc, prev_doc, new_temp.name, prev_temp.name)

    def apply_diffs(self):
        diffs = self.dmp.create_word_diffs(
            self.prev_doc.clean_text,
            self.current_doc.clean_text,
            ignore_special_chars=True,
        )
        deletes, inserts = self.dmp.get_diff_sections(diffs, page_breaks=False)
        for section in deletes:
            self.prev_doc.apply_word_spans(section.word_spans, method=CompareDoc.DELETE)
        for section in inserts:
            self.current_doc.apply_word_spans(section.word_spans, method=CompareDoc.INSERT)

    def compare(
        self, doc: RetrievedDocument | DocDocument, prev_doc: RetrievedDocument | DocDocument
    ):
        self._set_docs(doc, prev_doc)
        self._clean_doc_texts()
        self.apply_diffs()
        self._save_diff_pdfs(doc, prev_doc)
