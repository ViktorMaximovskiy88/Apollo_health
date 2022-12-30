from datetime import datetime
from random import random

import igraph
import pytest
import pytest_asyncio
from beanie import PydanticObjectId
from pydantic import Field

from backend.common.db.init import init_db
from backend.common.models.lineage import DocumentAnalysis
from backend.common.services.lineage.model.model import DocIndex, LineageModel


class BasicDocAnalysis(DocumentAnalysis):
    retrieved_document_id: PydanticObjectId = Field(default_factory=PydanticObjectId)
    doc_document_id: PydanticObjectId = Field(default_factory=PydanticObjectId)
    site_id: PydanticObjectId = PydanticObjectId()


@pytest_asyncio.fixture(autouse=True)
async def before_each_test():
    await init_db(mock=True, database_name=str(random()))


def incrementing_id():
    i = 0
    while True:
        yield PydanticObjectId(f"{i:024}")
        i += 1


@pytest.mark.asyncio
async def test_case_1():
    model = LineageModel()
    ids = incrementing_id()
    l1, l2, l3 = next(ids), next(ids), next(ids)
    analyses: list[DocumentAnalysis] = [
        BasicDocAnalysis(lineage_id=l1, final_effective_date=datetime(2020, 1, 1)),
        BasicDocAnalysis(lineage_id=l2, final_effective_date=datetime(2021, 1, 1)),
        BasicDocAnalysis(lineage_id=l1, final_effective_date=datetime(2023, 1, 1)),
        BasicDocAnalysis(lineage_id=l1, final_effective_date=datetime(2021, 1, 1)),
        BasicDocAnalysis(lineage_id=l3, final_effective_date=datetime(2022, 1, 1)),
        BasicDocAnalysis(lineage_id=l2, final_effective_date=datetime(2024, 1, 1)),
    ]
    lineages = model.group_by_lineage_id(analyses)
    for lineage in lineages:
        lineage_ids = set(doc.lineage_id for doc in lineage)
        assert len(lineage_ids) == 1
        dates = [doc.final_effective_date or datetime(0, 0, 0) for doc in lineage]
        assert dates == sorted(dates)


@pytest.mark.asyncio
async def test_case_2():
    model = LineageModel()
    ids = incrementing_id()
    l1, l2, l3 = next(ids), next(ids), next(ids)
    a1 = BasicDocAnalysis(lineage_id=l1, final_effective_date=datetime(2023, 1, 1))
    b1 = BasicDocAnalysis(lineage_id=l2, final_effective_date=datetime(2024, 1, 1))
    b2 = BasicDocAnalysis(lineage_id=l2, final_effective_date=datetime(2025, 1, 1))
    c1 = BasicDocAnalysis(lineage_id=l3, final_effective_date=datetime(2022, 1, 1))
    analyses: list[DocumentAnalysis] = [a1, b1, b2, c1]
    lineages = model.group_by_lineage_id(analyses)
    lineage_map = {lineage[0].doc_document_id: lineage for lineage in lineages}
    docs = DocIndex([a1, b1, c1])
    graph = igraph.Graph.Bipartite([0, 1, 1], edges=[])
    pairs, weights = [(0, 1)], [0.9]
    igraph.Graph.add_edges(graph, pairs, attributes={"weight": weights})

    model.match_lineage_graph(graph, docs, lineage_map)
    assert analyses[0].lineage_id == analyses[1].lineage_id == analyses[2].lineage_id
    assert analyses[1].confidence == 0.9
    assert analyses[0].lineage_id != analyses[3].lineage_id
