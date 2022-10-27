import logging
from pathlib import Path
from typing import Any, Tuple

import gensim
import numpy as np
import xgboost as xgb

logging.basicConfig(format="%(asctime)s : %(levelname)s : %(message)s", level=logging.INFO)

vector_size = 50
local_dir = Path(__file__).parent
vector_model = gensim.models.doc2vec.Doc2Vec.load(
    str(local_dir.joinpath("./doc_type_model/doc2vec_model.pkl").resolve())
)
xgb_model = xgb.XGBClassifier()
xgb_model.load_model(str(local_dir.joinpath("./doc_type_model/xgbmodel.json").resolve()))

doc_types = [
    "Authorization Policy",
    "Provider Guide",
    "Treatment Request Form",
    "Payer Unlisted Policy",
    "Covered Treatment List",
    "Regulatory Document",
    "Formulary",
    "Internal Reference",
    "Formulary Update",
    "NCCN Guideline",
    "Restriction List",
    "Review Committee Meetings",
]


def classify_doc_type(text: str) -> Tuple[str, float, Any]:
    tokens = gensim.utils.simple_preprocess(text)
    vector = vector_model.infer_vector(tokens).reshape((1, vector_size))
    probabilities = xgb_model.predict_proba(vector)[0]
    prediction_index = np.argmax(probabilities)

    confidence = probabilities[prediction_index]
    predicted_doc_type = doc_types[prediction_index]

    return (
        predicted_doc_type,
        confidence,
        vector,
    )
