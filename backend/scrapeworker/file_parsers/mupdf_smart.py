import statistics
from collections import Counter
from heapq import nlargest, nsmallest

import fitz

from backend.scrapeworker.common.utils import deburr, group_by_key
from backend.scrapeworker.file_parsers.base import FileParser


class MuPdfSmartParse(FileParser):
    def __init__(self, *args, **kwargs):
        super(MuPdfSmartParse, self).__init__(*args, **kwargs)
        self.row_number = 0
        self.doc = fitz.Document(self.file_path)
        self.pages = self.get_structure()
        self.parts = self.map_document_parts()
        self.process_lines()

        # table handle, later
        self.is_open_table = False
        self.table_index = 0
        self.table_col = 0
        self.table_row = 0

        x_coords = [part["origin_x"] for part in self.parts]
        y_coords = [part["origin_y"] for part in self.parts]
        styles = [part["style"] for part in self.parts]

        grouped = group_by_key(self.parts, "page_index")
        doc_stat_number = 10
        min_x = nsmallest(doc_stat_number, x_coords)
        max_x = nlargest(doc_stat_number, x_coords)

        min_y = nsmallest(doc_stat_number, y_coords)
        max_y = nlargest(doc_stat_number, y_coords)

        self.document_analysis = {
            "frequency_style": Counter(styles).most_common(doc_stat_number),
            "frequency_x": Counter(x_coords).most_common(doc_stat_number),
            "count_x": len(x_coords),
            "min_x": min_x,
            "max_x": max_x,
            "mean_x": statistics.mean(x_coords),
            "median_x": statistics.median(x_coords),
            "mode_x": statistics.multimode(x_coords),
            "frequency_y": Counter(y_coords).most_common(doc_stat_number),
            "count_y": len(y_coords),
            "min_y": min_y,
            "max_y": max_y,
            "mean_y": statistics.mean(y_coords),
            "median_y": statistics.median(y_coords),
            "mode_y": statistics.multimode(y_coords),
            "pages": [],
        }

        page_stat_count = 5
        for page_index, parts in grouped:
            parts_list = list(parts)
            x_coords = [part["origin_x"] for part in parts_list]
            y_coords = [part["origin_y"] for part in parts_list]
            styles = [part["style"] for part in self.parts]

            min_x = nsmallest(page_stat_count, x_coords)
            max_x = nlargest(page_stat_count, x_coords)

            min_y = nsmallest(page_stat_count, y_coords)
            max_y = nlargest(page_stat_count, y_coords)

            self.document_analysis["pages"].append(
                {
                    "page_index": page_index,
                    "frequency_style": Counter(styles).most_common(doc_stat_number),
                    "frequency_x": Counter(x_coords).most_common(page_stat_count),
                    "count_x": len(x_coords),
                    "min_x": min_x,
                    "max_x": max_x,
                    "mean_x": statistics.mean(x_coords),
                    "median_x": statistics.median(x_coords),
                    "mode_x": statistics.multimode(x_coords),
                    "frequency_y": Counter(y_coords).most_common(page_stat_count),
                    "count_y": len(y_coords),
                    "min_y": min_y,
                    "max_y": max_y,
                    "mean_y": statistics.mean(y_coords),
                    "median_y": statistics.median(y_coords),
                    "mode_y": statistics.multimode(y_coords),
                    "parts": list(parts_list),
                }
            )

        # self.document_analysis

        # header detection
        # canidates = []
        # for mode_y in self.document_analysis["mode_y"]:
        #     for page in self.document_analysis["pages"]:
        #         text = "".join(
        #             [part["text"] for part in page["parts"] if part["origin_y"] == mode_y]
        #         )
        #         print(text)

        # heading detection
        # h1 kinda thing (heading to not confuse header)

    async def get_info(self) -> dict[str, str]:
        return self.doc.metadata

    def get_structure(self, format="dict"):
        pages = []
        for page in self.doc:
            pages.append(page.get_text(format, sort=True))
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

    def map_span(self, span: dict):
        span["origin_x"] = span["origin"][0]
        span["origin_y"] = span["origin"][1]
        span["bbox_x0"] = span["bbox"][0]
        span["bbox_y0"] = span["bbox"][1]
        span["bbox_x1"] = span["bbox"][2]
        span["bbox_y1"] = span["bbox"][3]
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
        index = 0
        for page_index, page in enumerate(self.pages):
            text_blocks = [block for block in page["blocks"] if block["type"] == 0]
            for block_index, block in enumerate(text_blocks):
                for line_index, line in enumerate(block["lines"]):
                    # map with lookbehind and lookahead
                    spans = [self.map_span(span) for span in line["spans"]]
                    for span_index, span in enumerate(spans):
                        prev_span = None if span_index == 0 else spans[span_index - 1]
                        next_span = None if span_index == len(spans) - 1 else spans[span_index + 1]
                        span["index"] = index
                        span["is_subscript"] = self.is_subscript(span, prev_span, next_span)
                        span["is_superscript"] = self.is_superscript(span, prev_span, next_span)
                        span["page_index"] = page_index
                        span["block_index"] = block_index
                        span["line_index"] = line_index
                        span["span_index"] = span_index
                        span[
                            "style"
                        ] = f"{span['size']}|{span['flags']}|{span['font']}|{span['color']}"
                        span.pop("bbox")
                        span.pop("origin")
                        parts.append(span)
                        index += 1

        sorted_parts = sorted(
            parts,
            key=lambda x: (
                x["page_index"],
                x["origin_y"],
                x["origin_x"],
                x["block_index"],
            ),
        )
        return sorted_parts

    def set_cell_location(self, parts):
        coords = {}
        x_aligned = group_by_key(parts, "origin_x")
        for x_coord, x_parts in x_aligned:
            coords[x_coord] = {}
            y_aligned = group_by_key(list(x_parts), "origin_y")
            for y_coord, y_parts in y_aligned:
                coords[x_coord][y_coord] = list(y_parts)
        print(coords)

    def set_row_number(self, part, prev, next):
        # first page
        if not prev:
            self.row_number = 0
            return self.row_number

        # new page, so new line
        if prev["page_index"] != part["page_index"]:
            self.row_number += 1
            return self.row_number

        # last page and part
        tolerance = 1.5
        if (
            not next
            and (abs(prev["origin_y"] - part["origin_y"]) <= tolerance)
            and prev["page_index"] == part["page_index"]
        ):
            return self.row_number
        elif not next and (abs(prev["origin_y"] - part["origin_y"]) > tolerance):
            self.row_number += 1
            return self.row_number

        # we have both prev and next
        #  same line, would be set by prev, skip
        if (
            abs(prev["origin_y"] - part["origin_y"]) <= tolerance
            and part["page_index"] == prev["page_index"]
        ):
            return self.row_number
        elif (
            abs(prev["origin_y"] - part["origin_y"]) > tolerance
            and part["page_index"] == prev["page_index"]
        ):
            self.row_number += 1
            return self.row_number

    def process_lines(self):
        # TODO think on spces in scripts, and/or scrubbing
        parts = [
            part for part in self.parts if not (part["is_superscript"] or part["is_subscript"])
        ]

        for index, part in enumerate(parts):
            prev = None if index == 0 else parts[index - 1]
            next = None if index == len(parts) - 1 else parts[index + 1]
            part["row_number"] = self.set_row_number(part, prev, next)

        # self.set_cell_location(self.parts)

        self.parts = parts
        return parts

    def detect_header_footer(self):
        # group by page
        # find min y and max y
        # header = for all pages find duplicated or very similar text very near min y
        # footer = for all pages find duplicated or very similar text very near max y
        pass

    def get_text(self):
        text = ""
        prev_row_number = 0
        is_new_line = False
        for index, part in enumerate(self.parts):
            prev = None if index == 0 else self.parts[index - 1]
            next = None if index == len(self.parts) - 1 else self.parts[index + 1]

            is_new_line = prev_row_number != part["row_number"]

            if is_new_line:
                text += "\n"

            text += part["text"]
            prev_row_number = part["row_number"]

        print(text.strip())
