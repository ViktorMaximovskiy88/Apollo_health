import pandas as pd
import xlrd

from backend.scrapeworker.file_parsers.base import FileParser


class XlsParser(FileParser):
    async def get_text(self) -> str:
        dataframes = pd.read_excel(self.file_path, engine="xlrd", sheet_name=None)
        text = ""
        for _key, df in dataframes.items():
            text += f"{df.to_string(index=False)}\n\n"
        return text

    async def get_info(self):
        book: xlrd.Book = xlrd.open_workbook(self.file_path)
        metadata = {"user_name": book.user_name, "sheet_count": book.nsheets}
        return metadata

    def get_title(self, metadata) -> str | None:
        title = str(self.filename_no_ext)
        return title
