import pandas as pd


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


async def parse_metadata(temp_path, url) -> dict[str, str]:
    pass
