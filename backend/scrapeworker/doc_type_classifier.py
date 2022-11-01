import logging
from pathlib import Path
from typing import Any, Tuple

import fasttext
import gensim

logging.basicConfig(format="%(asctime)s : %(levelname)s : %(message)s", level=logging.INFO)

local_dir = Path(__file__).parent
fasttext_model = fasttext.load_model(
    str(local_dir.joinpath("./doc_type_model/fasttext_model.bin").resolve())
)


def classify_doc_type(text: str) -> Tuple[str, float, Any]:
    clean_text = " ".join(gensim.utils.simple_preprocess(text))
    vector = fasttext_model.get_sentence_vector(clean_text).tolist()
    prediction, confidence = fasttext_model.predict(clean_text)
    clean_pred = prediction[0].removeprefix("__label__").replace("-", " ")
    conf = confidence[0]
    return (
        clean_pred,
        conf,
        [vector],
    )
