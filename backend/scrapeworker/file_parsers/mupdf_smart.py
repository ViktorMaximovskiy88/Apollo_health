import fitz

from backend.scrapeworker.common.utils import deburr, group_by_key, normalize_spaces
from backend.scrapeworker.file_parsers.base import FileParser


class MuPdfSmartParse(FileParser):
    def __init__(self, *args, **kwargs):
        super(MuPdfSmartParse, self).__init__(*args, **kwargs)
        self.doc = fitz.Document(self.file_path)
        self.pages = self.get_structure()
        self.parts = []
        self.table_index = 0

    async def get_info(self) -> dict[str, str]:
        return self.doc.metadata

    def get_structure(self, format="dict"):
        pages = []
        for page in self.doc:
            pages.append(page.get_text(format))
        return pages

    def get_structure_json(self):
        # MuPDF serializes json better/easier then dict -> json.dumps
        # eat the perf as this is one off for testing
        pages = self.get_structure("json")
        return f"[{','.join(pages)}]"

    async def get_text(self):
        pdftext_out = ""
        for page in self.doc:
            text = page.get_text()
            pdftext_out += deburr(text.strip())
        return pdftext_out.strip()

    def get_title(self, metadata):
        title = metadata.get("title") or metadata.get("subject") or str(self.filename_no_ext)
        return title

    def detect_doc_elements(self):
        pass

    def detect_page_elements(self):
        pass

    def detect_page_header(self):
        # by position
        # by repetition
        # by font
        # by siblings
        # by exact edges
        # by fuzzy edges
        pass

    def same_font(self, span_a: dict, span_b: dict) -> bool:
        return span_a["font"] == span_b["font"]

    def same_size(self, span_a: dict, span_b: dict) -> bool:
        return span_a["size"] == span_b["size"]

    def same_color(self, span_a: dict, span_b: dict) -> bool:
        return span_a["color"] == span_b["color"]

    def same_flags(self, span_a: dict, span_b: dict) -> bool:
        return span_a["flags"] == span_b["flags"]

    def same_style(self, span_a: dict, span_b: dict) -> bool:
        return (
            self.same_color(span_a, span_b)
            and self.same_size(span_a, span_b)
            and self.same_font(span_a, span_b)
            and self.same_flags(span_a, span_b)
        )

    def same_line(self, span_a: dict, span_b: dict):
        (xa, ya) = span_a["origin"]
        (xb, yb) = span_b["origin"]
        return ya == yb

    def map_span(self, span: dict):
        span["origin_x"] = span["origin"][0]
        span["origin_y"] = span["origin"][1]
        span["bbox_x0"] = span["bbox"][0]
        span["bbox_y0"] = span["bbox"][1]
        span["bbox_x1"] = span["bbox"][2]
        span["bbox_y1"] = span["bbox"][3]
        span["scrubbed"] = deburr(span["text"])
        span["line_height"] = abs(span["ascender"]) + abs(span["descender"])
        return span

    def is_subscript(self, span: dict, prev: dict = None, next: dict = None):
        # i mean this is a bit open but cant compare... maybe styles analysis too
        if not (prev or next):
            return False

        if (
            prev
            and prev["origin_y"] < span["origin_y"]
            and prev["origin_y"] - span["origin_y"] < span["line_height"]
            and prev["font"] == span["font"]
            and prev["size"] > span["size"]
        ) or (
            next
            and next["origin_y"] < span["origin_y"]
            and next["origin_y"] - span["origin_y"] < span["line_height"]
            and next["font"] == span["font"]
            and next["size"] > span["size"]
        ):
            return True
        else:
            return False

    def is_superscript(self, span: dict, prev: dict = None, next: dict = None):
        # i mean this is a bit open but cant compare... maybe styles analysis too
        if not (prev or next):
            return False

        if (
            prev
            and prev["origin_y"] > span["origin_y"]
            and prev["font"] == span["font"]
            and prev["size"] > span["size"]
        ) or (
            next
            and next["origin_y"] > span["origin_y"]
            and next["font"] == span["font"]
            and next["size"] > span["size"]
        ):
            return True
        else:
            return False

    def map_document_parts(self):
        parts = []
        for page_index, page in enumerate(self.pages):
            text_blocks = [block for block in page["blocks"] if block["type"] == 0]
            for block_index, block in text_blocks):
                for line_index, line in enumerate(block["lines"]):
                    # map with lookbehind and lookahead
                    spans = [self.map_span(span) for span in line["spans"]]
                    for span_index, span in enumerate(spans):
                        prev_span = None if span_index == 0 else spans[span_index - 1]                        next_span = None if span_index == len(spans) - 1 else spans[span_index + 1]

                        span["is_subscript"] = self.is_subscript(span, prev_span, next_span)
                        span["is_superscript"] = self.is_superscript(span, prev_span, next_span)
                        span["page_index"] = page_index
                        span["block_index"] = block_index
                        span["line_index"] = line_index
                        span["span_index"] = span_index
                        span.pop("bbox")
                        span.pop("origin")
                        parts.append(span)

        return parts


    def is_table_row(self, part, prev, next):
        # i mean this is a bit open but cant compare... maybe styles analysis too
        if not (prev and next):
            return False

        return prev["origin_y"] == part["origin_y"] and next["origin_y"] == part["origin_y"] and part["page_index"] == prev["page_index"] and part["page_index"] == next["page_index"]


    def detect_table(self):
        table_row = None
        parts = self.parts
        for index, span in enumerate(parts):
            prev = None if index == 0 else parts[index - 1]
            next = None if index == len(parts) - 1 else parts[index + 1]

        return []



    def print_text(self, spans):
        text = ""
        for span in enumerate(spans):
            # print(page_index, block_index, line_index, span)
            print(span)
            if span["is_superscript"] or span["is_subscript"]:
                continue

            # options: remove unicode, subscript, superscript
            text += deburr(span["text"])

        print(text.strip())
