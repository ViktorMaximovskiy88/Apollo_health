import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.joinpath("../../..").resolve()))
import json
import os
import tempfile

import spacy

from backend.common.storage.client import ModelStorageClient

nlp = spacy.blank("en")
ruler = nlp.add_pipe("span_ruler", config={"spans_key": "sc", "phrase_matcher_attr": "LOWER"})

client = ModelStorageClient()
for line in client.read_lines("rxnorm/latest/rxnorm.jsonl"):
    obj = json.loads(line)
    for pattern in obj["aliases"]:
        ruler.add_patterns(
            [{"label": f"{obj['concept_id']}|{obj['canonical_name']}", "pattern": pattern}]
        )  # type: ignore

with tempfile.TemporaryDirectory() as tmpdir:
    nlp.to_disk(tmpdir)
    for root, dirs, files in os.walk(tmpdir):
        for local_path in files:
            folder = root.removeprefix(tmpdir).removeprefix("/")
            remote_path = f"rxnorm-span/latest/{folder}/{local_path}"
            client.write_object(remote_path, f"{root}/{local_path}")
