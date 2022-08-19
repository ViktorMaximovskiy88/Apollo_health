import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.joinpath("../../..").resolve()))
import json
import os
import tempfile

from scispacy.candidate_generation import create_tfidf_ann_index
from scispacy.linking_utils import KnowledgeBase

from backend.common.storage.client import ModelStorageClient

client = ModelStorageClient()
input_path = "rxnorm/data/RxNorm_full_06062022/RXNCONSO.RRF"

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

for line in client.read_lines(input_path):
    fields = line.split("|")
    rxcui = fields[h["RXCUI"]]
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

    record = data_by_rxcui.get(rxcui, None)
    if not record:
        record = {"concept_id": rxcui, "aliases": set(), "types": set()}
        data_by_rxcui[rxcui] = record

    if term_type in ["SY", "ET", "TMSY", "PSN"] or source != "RXNORM":
        record["aliases"].add(name)
    else:
        record["canonical_name"] = name
        record["aliases"].add(name)
        record["types"].add(term_type)

with tempfile.NamedTemporaryFile("w", suffix="jsonl") as file:
    for record in data_by_rxcui.values():
        if "canonical_name" not in record:
            continue

        record["aliases"] = list(record["aliases"])
        record["types"] = list(record["types"])
        file.write(json.dumps(record))
        file.write("\n")
    client.write_object("rxnorm/latest/rxnorm.jsonl", file.name)

    with tempfile.TemporaryDirectory() as tmpdir:
        create_tfidf_ann_index(tmpdir, KnowledgeBase(file.name))
        for local_path in os.listdir(tmpdir):
            remote_path = f"rxnorm/latest/{local_path}"
            client.write_object(remote_path, f"{tmpdir}/{local_path}")
