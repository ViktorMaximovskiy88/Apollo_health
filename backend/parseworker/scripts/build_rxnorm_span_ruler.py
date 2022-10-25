import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.joinpath("../../..").resolve()))
import json
import pathlib
import typer

import spacy

def main(output_folder: pathlib.Path = typer.Argument(None)):

    nlp = spacy.blank("en")
    ruler = nlp.add_pipe("span_ruler", config={"spans_key": "sc", "phrase_matcher_attr": "LOWER"})

    rxnorm_file_path = output_folder.joinpath("rxnorm", "rxnorm.jsonl")

    with open(rxnorm_file_path, 'r') as file: 
        lines = file.readlines()
        for line in lines:
            obj = json.loads(line)
            for pattern in obj["aliases"]:
                ruler.add_patterns(  # type: ignore
                    [{"label": f"{obj['concept_id']}|{obj['canonical_name']}", "pattern": pattern}]
                )

    rxnorm_span_base_path = output_folder.joinpath("rxnorm-span")
    rxnorm_span_base_path.mkdir(exist_ok=True, parents=True)
    nlp.to_disk(rxnorm_span_base_path)

if __name__ == "__main__":
    typer.run(main)