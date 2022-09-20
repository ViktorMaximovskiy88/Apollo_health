import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.joinpath("../../..").resolve()))
import os

import typer
from openpyxl import load_workbook

from backend.common.storage.client import ModelStorageClient


def main(excel_path: str):
    client = ModelStorageClient()
    wb = load_workbook(excel_path)

    lines = []
    for sheet_name in ["RxNorm_XREF", "Additional DrugIDs"]:
        h = {}
        for line in wb[sheet_name].values:  # type: ignore
            if not h:
                h = {v: i for i, v in enumerate(line)}
                continue
            rxcui = ""
            if "RXCUI" in h:
                rxcui = str(line[h["RXCUI"]] or "")
            drugid = str(line[h["drugid"]] or "")
            drug_name = str(line[h["DrugName"]] or "")
            drug_description = str(line[h["DrugDescription"]] or "")
            line = "|".join([drugid, rxcui, drug_name, drug_description])
            lines.append(line)

    file_name = os.path.basename(excel_path).removesuffix(".xlsx")
    upload_location = f"rxnorm/data/{file_name}.txt"
    client.write_object_mem(upload_location, "\n".join(lines))


if __name__ == "__main__":
    typer.run(main)
