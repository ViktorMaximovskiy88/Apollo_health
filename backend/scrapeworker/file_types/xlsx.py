import pandas as pd
from openpyxl import load_workbook


def xlsx_to_text(temp_path: str):
    dataframes = pd.read_excel(
        temp_path,
        engine="openpyxl",
        sheet_name=None,
    )
    text = ""
    for _key, df in dataframes.items():
        text += f"{df.to_string(index=False)}\n\n"
    return text


def parse_metadata(temp_path: str, url: str | None = None) -> dict[str, str]:
    workbook = load_workbook(temp_path)
    props = vars(workbook.properties)
    return props
