import pandas as pd
from openpyxl import load_workbook
from backend.scrapeworker.file_parsers.base import FileParser


class XlsxParser(FileParser):
    async def get_text(self) -> str:
        dataframes = pd.read_excel(
            self.file_path,
            engine="openpyxl",
            sheet_name=None,  # type: ignore
        )
        text = ""
        for _key, df in dataframes.items():
            text += f"{df.to_string(index=False)}\n\n"
        return text

    async def get_info(self) -> dict[str, str]:
        workbook = load_workbook(self.file_path)
        props = vars(workbook.properties)  # type: ignore
        return props

    def get_title(self, metadata) -> str | None:
        title = (
            metadata["title"]
            or metadata["subject"]
            or metadata["category"]
            or str(self.filename_no_ext)
        )
        return title
