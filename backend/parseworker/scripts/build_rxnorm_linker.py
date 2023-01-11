import csv
import io
import json
import os
import pathlib
import sys
from contextlib import contextmanager
from pathlib import Path
from zipfile import ZipFile

import spacy
import typer
from scispacy.candidate_generation import create_tfidf_ann_index
from scispacy.linking_utils import KnowledgeBase

sys.path.append(str(Path(__file__).parent.joinpath("../../..").resolve()))
from backend.common.storage.client import ModelStorageClient


@contextmanager
def read_s3_zip(client, input_path):
    with client.read_object_to_tempfile(input_path) as tempfile:
        with ZipFile(tempfile) as zipfile:
            yield zipfile


def zip_csv(zip, filename):
    with zip.open(filename) as file:
        for line in csv.DictReader(
            io.TextIOWrapper(file), delimiter="|", doublequote=False, escapechar="\\"
        ):
            yield line


def get_priority_from_row(row):
    ntm = int(row["PriorityDrug"])
    in_par = int(row["PARDrug"])
    new_ind = int(row["Mapped_to_NewIndication"])
    if new_ind:
        return 3
    if ntm:
        return 2
    if in_par:
        return 1
    return 0


def main(output_folder: pathlib.Path = typer.Argument(None)):
    client = ModelStorageClient()
    xref_path = "models/upload"
    latest = ""
    for obj in client.bucket.objects.filter(Prefix=xref_path):
        if obj.key > latest and obj.key.startswith("models/upload/RxNorm-Xref"):
            latest = obj.key
    latest = latest.removeprefix("models/")

    data = []
    ind_patterns = []
    if not output_folder:
        folder = os.path.splitext(os.path.basename(latest))[0][-10:].replace("-", "")
        output_folder = pathlib.Path(f"./{folder}.1")

    print(f"Fitting {latest} data, output to {output_folder}")

    with read_s3_zip(client, latest) as zip:
        for row in zip_csv(zip, "IndicationSearchTerms.csv"):
            term = row["Term"]
            id = row["IndicationId"]
            name = row["IndicationName"]
            ind_patterns.append({"label": f"{name}|{term}|{id}", "pattern": term})

        for row in zip_csv(zip, "RxNorm_Xref.csv"):
            drugid = row["drugid"]
            rxcui = row["RXCUI"]
            name = row["DrugName"]
            description = row["DrugDescription"]
            rxnorm = row["RxNORM_STR"]
            priority = get_priority_from_row(row)

            record = {
                "concept_id": f"{drugid}:{priority}|{rxcui}",
                "canonical_name": name,
                "aliases": set([description, rxnorm]),
                "types": set(),
            }
            data.append(record)

        for row in zip_csv(zip, "RxNorm_Xref_Missing.csv"):
            drugid = row["drugid"]
            name = row["DrugName"]
            description = row["DrugDescription"]
            priority = get_priority_from_row(row)
            record = {
                "concept_id": f"{drugid}:{priority}",
                "canonical_name": name,
                "aliases": set([description]),
                "types": set(),
            }
            data.append(record)

    rxnorm_base_path = output_folder / "rxnorm"
    rxnorm_base_path.mkdir(exist_ok=True, parents=True)

    therapy_patterns = []
    rxnorm_file_path = rxnorm_base_path / "rxnorm.jsonl"
    with open(rxnorm_file_path, "w") as file:
        for record in data:
            record["aliases"] = list(record["aliases"])
            record["types"] = list(record["types"])

            label = f"{record['concept_id']}|{record['canonical_name']}"
            for alias in record["aliases"]:
                therapy_patterns.append({"label": label, "pattern": alias})

            file.write(json.dumps(record))
            file.write("\n")

    # TFIDF
    create_tfidf_ann_index(str(rxnorm_base_path), KnowledgeBase(str(rxnorm_file_path)))

    # Span Ruler
    config = {"spans_key": "sc", "phrase_matcher_attr": "LOWER"}
    rxnorm_span_base_path = output_folder / "rxnorm-span"
    rxnorm_span_base_path.mkdir(exist_ok=True, parents=True)
    ther_span = spacy.blank("en")
    ther_span.add_pipe("span_ruler", config=config).add_patterns(therapy_patterns)  # type: ignore
    ther_span.to_disk(rxnorm_span_base_path)

    # Indications
    indication = spacy.blank("en")
    indication.max_length = 300_000_000
    indication.add_pipe("span_ruler", config=config).add_patterns(ind_patterns)  # type: ignore

    ind_base_path = output_folder.joinpath("indications")
    ind_base_path.mkdir(exist_ok=True, parents=True)
    indication.to_disk(ind_base_path)


if __name__ == "__main__":
    typer.run(main)
