import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.joinpath("../../..").resolve()))
import json
import pathlib
import typer

from scispacy.candidate_generation import create_tfidf_ann_index
from scispacy.linking_utils import KnowledgeBase

from backend.common.storage.client import ModelStorageClient


def main(output_folder: pathlib.Path = typer.Argument(None)):

    client = ModelStorageClient()
    input_path = "rxnorm/data/RxNorm_full_09062022/RXNCONSO.RRF"
    xref_path = "rxnorm/data/RxNorm-Xref-2022-08-30.txt"

    header_line = [
        "RXCUI",
        "LAT",
        "TS",
        "LUI",
        "STT",
        "SUI",
        "ISPREF",
        "RXAUI",
        "SAUI",
        "SCUI",
        "SDUI",
        "SAB",
        "TTY",
        "CODE",
        "STR",
        "SRL",
        "SUPPRESS",
        "CVF",
    ]
    h = {value: index for (index, value) in enumerate(header_line)}
    data_by_rxcui = {}

    xref_header = ["DRUGID", "RXCUI", "NAME", "DESCRIPTION"]
    xh = {value: index for (index, value) in enumerate(xref_header)}
    for line in client.read_lines(xref_path):
        fields = line.split("|")
        drugid = fields[xh["DRUGID"]]
        rxcui = fields[xh["RXCUI"]]
        name = fields[xh["NAME"]]
        description = fields[xh["DESCRIPTION"]]
        record = {
            "concept_id": f"{drugid}|{rxcui}",
            "canonical_name": name,
            "aliases": set([description]),
            "types": set(),
        }
        data_by_rxcui.setdefault(rxcui, {})
        data_by_rxcui[rxcui][drugid] = record


    for line in client.read_lines(input_path):
        fields = line.split("|")
        rxcui = fields[h["RXCUI"]]
        if rxcui not in data_by_rxcui:
            continue

        term_type = fields[h["TTY"]]
        name = fields[h["STR"]]
        suppress = fields[h["SUPPRESS"]]
        source = fields[h["SAB"]]

        if suppress in ["Y", "O", "E"]:
            continue
        if term_type in ["DF", "ET", "DFG", "SBDG"]:
            continue
        if source != "RXNORM":
            continue

        data_by_drug_id = data_by_rxcui[rxcui]
        for drugid, record in data_by_drug_id.items():
            record["aliases"].add(name)

    rxnorm_base_path = output_folder.joinpath("rxnorm")
    rxnorm_base_path.mkdir(exist_ok=True, parents=True)

    rxnorm_file_path = rxnorm_base_path.joinpath("rxnorm.jsonl")

    with open(rxnorm_file_path, 'w') as file:
        for data_by_drug_id in data_by_rxcui.values():
            for record in data_by_drug_id.values():
                record["aliases"] = list(record["aliases"])
                record["types"] = list(record["types"])
                file.write(json.dumps(record))
                file.write("\n")
    create_tfidf_ann_index(rxnorm_base_path, KnowledgeBase(str(rxnorm_file_path)))


if __name__ == "__main__":
    typer.run(main)
