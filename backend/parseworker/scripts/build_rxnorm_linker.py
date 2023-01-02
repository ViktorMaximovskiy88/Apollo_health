import csv
import io
import sys
from contextlib import contextmanager
from pathlib import Path
from zipfile import ZipFile

sys.path.append(str(Path(__file__).parent.joinpath("../../..").resolve()))
import json
import pathlib

import typer
from scispacy.candidate_generation import create_tfidf_ann_index
from scispacy.linking_utils import KnowledgeBase

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


def main(output_folder: pathlib.Path = typer.Argument(None)):
    client = ModelStorageClient()
    xref_path = "models/upload"
    latest = ""
    for obj in client.bucket.objects.filter(Prefix=xref_path):
        if obj.key > latest and obj.key.startswith("models/upload/RxNorm-Xref"):
            latest = obj.key
    latest = latest.removeprefix("models/")

    ntm = {line.strip() for line in open(Path(__file__).parent.joinpath("ntm.txt"))}

    data = []
    print(f"Fitting {latest} data")
    with read_s3_zip(client, latest) as zip:
        for row in zip_csv(zip, "RxNorm_Xref.csv"):
            drugid = row["drugid"]
            rxcui = row["RXCUI"]
            name = row["DrugName"]
            description = row["DrugDescription"]
            rxnorm = row["RxNORM_STR"]
            priority = 2 if drugid in ntm else 0
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
            priority = 2 if drugid in ntm else 0
            record = {
                "concept_id": f"{drugid}:{priority}",
                "canonical_name": name,
                "aliases": set([description]),
                "types": set(),
            }
            data.append(record)

    rxnorm_base_path = output_folder.joinpath("rxnorm")
    rxnorm_base_path.mkdir(exist_ok=True, parents=True)

    rxnorm_file_path = rxnorm_base_path.joinpath("rxnorm.jsonl")

    with open(rxnorm_file_path, "w") as file:
        for record in data:
            record["aliases"] = list(record["aliases"])
            record["types"] = list(record["types"])
            file.write(json.dumps(record))
            file.write("\n")
    create_tfidf_ann_index(str(rxnorm_base_path), KnowledgeBase(str(rxnorm_file_path)))


if __name__ == "__main__":
    typer.run(main)
