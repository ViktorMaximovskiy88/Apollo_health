import logging
from functools import cache
from pathlib import Path
from typing import Any, Tuple

import fasttext
import gensim

from backend.common.core.enums import DocumentType
from backend.scrapeworker.doc_type_matcher import DocTypeMatcher

logging.basicConfig(format="%(asctime)s : %(levelname)s : %(message)s", level=logging.INFO)
local_dir = Path(__file__).parent


@cache
def get_model(dir: Path):
    return fasttext.load_model(str(dir.joinpath("./doc_type_model/fasttext_model.bin").resolve()))


def classify_doc_type(raw_text: str) -> Tuple[str, float, Any]:
    clean_text = " ".join(gensim.utils.simple_preprocess(raw_text))
    fasttext_model = get_model(local_dir)
    vector = fasttext_model.get_sentence_vector(clean_text).tolist()
    prediction, confidence = fasttext_model.predict(clean_text)
    clean_pred = prediction[0].removeprefix("__label__").replace("-", " ")

    # doc type was renamed; lets do a mapping for this one; can be dropped with new model
    # trained on new Doc Type list
    # "Covered Treatment List" -> "Medical Coverage List"
    clean_pred = (
        DocumentType.MedicalCoverageList if clean_pred == "Covered Treatment List" else clean_pred
    )
    conf = confidence[0]
    return (clean_pred, conf, [vector])


def guess_doc_type(
    raw_text: str, raw_link_text: str, raw_url: str, raw_name: str
) -> Tuple[str, float, Any]:

    doc_type_match = DocTypeMatcher(raw_text, raw_link_text, raw_url, raw_name).exec()

    # always classify for vectors
    _doc_type, _confidence, doc_vectors = classify_doc_type(raw_text)

    if not doc_type_match:
        return _doc_type, _confidence, doc_vectors
    else:
        return doc_type_match.document_type, doc_type_match.confidence, doc_vectors
