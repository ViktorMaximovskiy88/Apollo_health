import logging
from pathlib import Path
from typing import Any, Tuple

import fasttext
import gensim

from backend.scrapeworker.doc_type_matcher import DocTypeMatcher

logging.basicConfig(format="%(asctime)s : %(levelname)s : %(message)s", level=logging.INFO)
local_dir = Path(__file__).parent


def get_model(dir: str):
    global _model
    if _model:
        return _model
    _model = fasttext.load_model(
        str(Path.joinpath("./doc_type_model/fasttext_model.bin").resolve())
    )
    return _model


def classify_doc_type(text: str) -> Tuple[str, float, Any]:
    fasttext_model = get_model(local_dir)
    vector = fasttext_model.get_sentence_vector(text).tolist()
    prediction, confidence = fasttext_model.predict(text)
    clean_pred = prediction[0].removeprefix("__label__").replace("-", " ")
    conf = confidence[0]
    return (
        clean_pred,
        conf,
        [vector],
    )


def guess_doc_type(text: str) -> Tuple[str, float, Any]:
    clean_text = " ".join(gensim.utils.simple_preprocess(text))
    doc_type = DocTypeMatcher(clean_text)
    confidence = 100

    # always classify for vectors
    _doc_type, _confidence, doc_vectors = classify_doc_type(text)

    # reassign to model result if we dont have a guess
    if not doc_type:
        doc_type = _doc_type
        confidence = _confidence

    return doc_type, confidence, doc_vectors
