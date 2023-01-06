import asyncio
import math
from collections import defaultdict
from datetime import datetime
from functools import cached_property
from itertools import combinations, pairwise, product
from pathlib import Path
from typing import Generator

import igraph as ig
import numpy as np
import xgboost
from beanie import PydanticObjectId
from tqdm import tqdm

from backend.common.db.init import init_db
from backend.common.models.lineage import DocumentAnalysis
from backend.common.services.lineage.model.preprocessor import LineagePreprocessor


class DocIndex:
    """
    Simple wrapper around a list of DocumentAnalysis objects that allows us to
    get the index of a document in the list by it's id, and vice versa.
    """

    def __init__(self, docs: list[DocumentAnalysis]) -> None:
        self.doc_analyses_by_idx: dict[PydanticObjectId | None, int] = {}
        self.docs = docs
        for i, doc in enumerate(docs):
            self.doc_analyses_by_idx[doc.doc_document_id] = i

    def to_idx(self, doc: DocumentAnalysis):
        return self.doc_analyses_by_idx[doc.doc_document_id]

    def to_doc(self, idx: int | None):
        if idx is None:
            raise Exception("Must pass in valid Index")
        return self.docs[idx]

    def __len__(self):
        return len(self.docs)


class LineageModel:
    def __init__(self, disable_progress=True) -> None:
        self.preprocessor = LineagePreprocessor()
        self.disable_progress = disable_progress

    def add_documents_to_lineages(
        self,
        new_doc_analyses: list[DocumentAnalysis],
        old_doc_analyses: list[DocumentAnalysis] = [],
    ) -> list[list[DocumentAnalysis]]:
        old_lineages = self.group_by_lineage_id(old_doc_analyses)
        new_lineages = self.lineage_documents(new_doc_analyses)
        self.merge_lineages(old_lineages, new_lineages)
        return new_lineages

    def group_by_lineage_id(
        self, doc_analyses: list[DocumentAnalysis]
    ) -> list[list[DocumentAnalysis]]:
        lineages: dict[PydanticObjectId | None, list[DocumentAnalysis]] = defaultdict(list)
        for doc in doc_analyses:
            lineages[doc.lineage_id].append(doc)
        for lineage in lineages.values():
            lineage.sort(key=lambda doc: doc.final_effective_date or datetime(0, 0, 0))
        return list(lineages.values())

    def create_analyses_graph(
        self,
        graph: ig.Graph,
        pair_generator: Generator[tuple[DocumentAnalysis, DocumentAnalysis], None, None],
        docs: DocIndex,
    ):
        b = 0
        batch_size = 100
        input = np.zeros((batch_size, self.preprocessor.n_columns), dtype=np.float32)
        pairs = np.zeros((batch_size, 2), dtype=np.int32)
        for docf1, docf2 in pair_generator:
            if self.obvious_mismatch(docf1, docf2):
                continue
            pairs[b][0] = docs.to_idx(docf1)
            pairs[b][1] = docs.to_idx(docf2)
            input[b] = self.preprocessor.preprocess(docf1, docf2)
            b += 1
            if b == batch_size:
                self.update_graph(input, pairs, graph)
                b = 0
        self.update_graph(input[:b], pairs[:b], graph)
        return graph

    def merge_lineages(
        self,
        old_lineages: list[list[DocumentAnalysis]],
        new_lineages: list[list[DocumentAnalysis]],
    ):
        def pair_generator():
            pairs = tqdm(
                product(old_lineages, new_lineages),
                total=len(old_lineages) * len(new_lineages),
                disable=self.disable_progress,
            )
            for old_lineage, new_lineage in pairs:
                yield old_lineage[-1], new_lineage[0]

        new_lineage_map: dict[PydanticObjectId | None, list[DocumentAnalysis]] = {
            new_lineage[0].doc_document_id: new_lineage for new_lineage in new_lineages
        }
        docs = DocIndex([doc[-1] for doc in old_lineages] + [doc[0] for doc in new_lineages])
        bools = [0 for _ in old_lineages] + [1 for _ in new_lineages]
        graph = ig.Graph.Bipartite(bools, edges=[])
        graph = self.create_analyses_graph(graph, pair_generator(), docs)

        self.match_lineage_graph(graph, docs, new_lineage_map)

    def match_lineage_graph(
        self,
        graph: ig.Graph,
        docs: DocIndex,
        new_lineage_map: dict[PydanticObjectId | None, list[DocumentAnalysis]],
    ):
        matches = graph.maximum_bipartite_matching().matching or []
        for node, match in enumerate(matches):
            if match != -1:
                old_doc = docs.to_doc(node)
                new_doc = docs.to_doc(match)
                lineage = new_lineage_map.pop(new_doc.doc_document_id, None)
                if not lineage:
                    continue

                for doc in lineage:
                    doc.is_current_version = False
                    doc.lineage_id = old_doc.lineage_id
                    if doc == new_doc:
                        doc.previous_doc_doc_id = old_doc.doc_document_id
                        doc.confidence = float(graph[match, node])
                lineage[-1].is_current_version = True

    def lineage_documents(self, doc_analyses: list[DocumentAnalysis]):
        docs = DocIndex(doc_analyses)

        def pair_generator():
            n_pairs = math.comb(len(doc_analyses), 2)
            for docf1, docf2 in tqdm(
                combinations(doc_analyses, 2), total=n_pairs, disable=self.disable_progress
            ):
                yield docf1, docf2

        graph = ig.Graph(len(docs))
        # n choose k means 800 docs will have to do 319,600 comparisons
        # just don't bother, each doc will be its own lineage
        if len(doc_analyses) < 800:
            graph = self.create_analyses_graph(graph, pair_generator(), docs)
        cc = graph.connected_components()

        lineages: list[list[DocumentAnalysis]] = []
        for doc_idxs in cc:
            lineage = [docs.to_doc(doc_idx) for doc_idx in doc_idxs]
            lineage_id = PydanticObjectId()
            lineage.sort(key=lambda doc: doc.final_effective_date or datetime(0, 0, 0))

            for d in lineage:
                d.lineage_id = lineage_id
                d.is_current_version = False

            lineage[0].previous_doc_doc_id = None
            for d1, d2 in pairwise(lineage):
                d2.confidence = float(graph[docs.to_idx(d1), docs.to_idx(d2)])
                d2.previous_doc_doc_id = d1.doc_document_id
            lineage[-1].is_current_version = True

            lineages.append(lineage)
        return lineages

    def obvious_mismatch(self, docf1: DocumentAnalysis, docf2: DocumentAnalysis) -> bool:
        if docf1.document_type != docf2.document_type:
            return True

        if docf1.file_size and docf2.file_size:
            ratio = docf1.file_size / docf2.file_size
            if ratio > 2 or ratio < 0.5:
                return True

        if docf1.token_count and docf2.token_count:
            ratio = docf1.token_count / docf2.token_count
            if ratio > 2 or ratio < 0.5:
                return True

        return False

    def update_graph(self, input, pairs, graph: ig.Graph):
        predict = self.model.predict_proba(input)
        if not predict.any():
            return
        prediction_mask = predict[:, 1] > 0.5
        weights = predict[prediction_mask][:, 1]
        matching_pairs = pairs[prediction_mask]
        ig.Graph.add_edges(graph, matching_pairs, attributes={"weight": weights})

    @cached_property
    def model(self):
        model = xgboost.XGBClassifier()
        folder = Path(__file__).parent
        model.load_model(folder / "lineage_model.bin")
        return model


if __name__ == "__main__":

    async def main():
        await init_db()
        prev_path = "prev_doc_analyses.json.txt"
        new_path = "new_doc_analyses.json.txt"
        old_docs = [DocumentAnalysis.parse_raw(line.strip()) for line in open(prev_path)]
        new_docs = [DocumentAnalysis.parse_raw(line.strip()) for line in open(new_path)]
        model = LineageModel(disable_progress=False)
        lineages = model.add_documents_to_lineages(new_docs, old_docs)
        for lineage in lineages:
            lineage_id = lineage[0].lineage_id
            print(lineage_id, [doc.name for doc in lineage])

    asyncio.run(main())
