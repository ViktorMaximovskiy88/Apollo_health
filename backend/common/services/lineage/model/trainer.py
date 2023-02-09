import asyncio
import math
import os
import pickle
from functools import cached_property
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
import xgboost
from sklearn.metrics import f1_score, roc_auc_score, roc_curve
from sklearn.model_selection import train_test_split
from tqdm import tqdm

from backend.common.db.init import init_db
from backend.common.models.document_analysis import DocumentAnalysis
from backend.common.services.lineage.model.preprocessor import LineagePreprocessor


class LineageModelTrainer:
    def __init__(self, input_folder: str) -> None:
        self.input_folder = input_folder
        self.random_state = np.random.RandomState(seed=6855520)
        self.preprocessor = LineagePreprocessor()

    @staticmethod
    def disk_cached(cachefile: str):
        def decorator(fn):
            def wrapped(*args, **kwargs):
                cachepath = os.path.expanduser(cachefile)
                if os.path.exists(cachepath):
                    with open(cachepath, "rb") as cachehandle:
                        print("using cached result from '%s'" % cachefile)
                        return pickle.load(cachehandle)
                res = fn(*args, **kwargs)
                with open(cachepath, "wb") as cachehandle:
                    print("saving result to cache '%s'" % cachefile)
                    pickle.dump(res, cachehandle)
                return res

            return wrapped

        return decorator

    @disk_cached("~/lineage_data.pkl")
    def create_X_y(self):
        asyncio.run(init_db())

        datasets = []
        with os.scandir(self.input_folder) as it:
            for entry in it:
                docs = [DocumentAnalysis.parse_raw(line) for line in open(entry.path)]
                n_rows = math.comb(len(docs), 2)
                X = np.zeros((n_rows, self.preprocessor.n_columns), dtype=np.float32)
                y = np.zeros(n_rows, dtype=np.bool_)
                for n, (doc1, doc2) in enumerate(tqdm(combinations(docs, 2), total=n_rows)):
                    X[n] = self.preprocessor.preprocess(doc1, doc2)
                    y[n] = int(doc1.lineage_id == doc2.lineage_id)
                datasets.append((X, y))
        X = np.concatenate([X for X, _ in datasets])
        y = np.concatenate([y for _, y in datasets])

        return X, y

    def train(self):
        model = xgboost.XGBClassifier(
            n_estimators=200,
            early_stopping_rounds=30,
            eval_metric="map",
            random_state=self.random_state,
            learning_rate=0.3,
            max_depth=8,
        )
        (X_train, y_train), (X_val, y_val), _ = self.load_data
        model.fit(X_train, y_train, eval_set=[(X_val, y_val)])

        folder = Path(__file__).parent
        model.save_model(folder / "lineage_model.bin")

    @cached_property
    def load_data(self):
        X, y = self.create_X_y()
        X_train_val, X_test, y_train_val, y_test = train_test_split(
            X, y, test_size=0.01, random_state=self.random_state
        )
        X_train, X_val, y_train, y_val = train_test_split(
            X_train_val, y_train_val, test_size=0.1, random_state=self.random_state
        )
        return (X_train, y_train), (X_val, y_val), (X_test, y_test)

    def assess_model(self):
        _, (X_val, y_val), _ = self.load_data
        path = Path(__file__).parent / "lineage_model.bin"
        model = xgboost.XGBClassifier()
        model.load_model(path)
        y_val_predict = model.predict_proba(X_val)

        roc_auc = roc_auc_score(y_val, y_val_predict[:, 1])
        _, _, thresholds = roc_curve(y_val, y_val_predict[:, 1])

        thresholds = np.linspace(0, 1, 100)
        f1s = [f1_score(y_val, y_val_predict[:, 1] > t) for t in thresholds]
        ix = np.argmax(f1s)
        f1 = f1s[ix]
        threshold = thresholds[ix]
        print(roc_auc, threshold, f1)

        fi = []
        feature_importance = model.feature_importances_
        for feature, importance in enumerate(feature_importance):
            fi.append((importance, feature))
        fi.sort(reverse=True)
        for importance, feature in fi[:10]:
            print(f"{importance:.2f} {self.preprocessor.column_names[feature]}")

        confusion_matrix = pd.crosstab(
            y_val, y_val_predict[:, 1] > threshold, rownames=["Actual"], colnames=["Predicted"]
        )
        print(confusion_matrix)

        return threshold


if __name__ == "__main__":
    import click

    @click.command()
    @click.option("--path", required=True)
    @click.option("--train", is_flag=True)
    def main(path, train):
        trainer = LineageModelTrainer(path)
        if train:
            trainer.train()
        trainer.assess_model()

    main()
