import asyncio
import copy
import json
import re
from typing import Any, Generic, TypeVar

from beanie import PydanticObjectId
from beanie.odm.queries.aggregation import AggregationQuery
from beanie.odm.queries.find import FindMany
from beanie.odm.utils.projection import get_projection
from dateutil import parser
from fastapi import Request

from backend.common.models.base_document import BaseModel

# Ideally this would be bound to BaseDocument, but beanie type inference
# chokes when attempting to identify collection
T = TypeVar("T")


class TableSortInfo(BaseModel):
    name: str
    dir: int


# can be dates or numbers but we parse elsewhere
class RangeValue(BaseModel):
    start: str
    end: str


class TableFilterInfo(BaseModel):
    name: str
    operator: str
    type: str
    value: str | list[str] | RangeValue | None


class TableQueryResponse(BaseModel, Generic[T]):
    data: list[T]
    total: int


def get_query_json_list(arg: str, type):
    def func(request: Request):
        value_str = request.query_params.get(arg, None)
        if value_str:
            values: list[type] = json.loads(value_str)
            if issubclass(type, BaseModel):
                return [type.parse_obj(v) for v in values]
            return values
        else:
            return []

    return func


def transform_value(
    filter_value: str,
    filter_type: str,
):
    if filter_type == "number":
        value = float(filter_value)
    elif filter_type == "date":
        value = parser.parse(filter_value)
    elif filter_type == "boolean":
        value = filter_value.lower() == "true"
    else:
        value = filter_value

    try:
        value = PydanticObjectId(value)
    except Exception:
        pass

    return value


def _prepare_table_query(
    sorts: list[TableSortInfo] = [],
    filters: list[TableFilterInfo] = [],
) -> tuple[list[dict], list[tuple[str, int]]]:
    match = []
    for filter in filters:
        if not filter.value and filter.operator not in [
            "empty",
            "notEmpty",
            "leq",
            "notinlist",
            "neq",
        ]:
            continue

        if filter.value is None:
            filter.value = ""

        if isinstance(filter.value, list):
            value = [transform_value(value, filter.type) for value in filter.value]
        elif isinstance(filter.value, RangeValue):
            value = [
                transform_value(filter.value.start, filter.type),
                transform_value(filter.value.end, filter.type),
            ]
        else:
            value = transform_value(filter.value, filter.type)

        if filter.operator == "textcontains":
            match.append({"$text": {"$search": value}})
        if filter.operator == "textnotContains":
            match.append({"$text": {"$search": f'-"{value}"'}})
        if filter.operator == "contains":
            match.append({filter.name: {"$regex": re.escape(value), "$options": "i"}})
        if filter.operator == "notContains":
            match.append({filter.name: {"$not": {"$regex": re.escape(value), "$options": "i"}}})
        if filter.operator == "startsWith":
            match.append({filter.name: {"$regex": f"^{re.escape(value)}", "$options": "i"}})
        if filter.operator == "endsWith":
            match.append({filter.name: {"$regex": f"{re.escape(value)}$", "$options": "i"}})
        if filter.operator == "eq" or filter.operator == "leq":
            if filter.operator == "eq" and isinstance(value, list):
                match.append({filter.name: {"$in": value}})
            else:
                match.append({filter.name: value})
        if filter.operator == "neq" or filter.operator == "nleq":
            if filter.operator == "neq" and isinstance(value, list):
                match.append({filter.name: {"$nin": value}})
            else:
                match.append({filter.name: {"$ne": value if value else None}})

        if filter.operator == "notinlist":
            match.append({filter.name: {"$nin": value if value else []}})
        if filter.operator == "empty":
            match.append({filter.name: {"$in": [None, ""]}})
        if filter.operator == "notEmpty":
            match.append({filter.name: {"$exists": True, "$nin": [None, ""]}})
        if filter.operator in ["gt", "gte", "lt", "lte"]:
            match.append({filter.name: {f"${filter.operator}": value}})
        if filter.operator == "after":
            match.append({filter.name: {"$gt": value}})
        if filter.operator == "afterOrOn":
            match.append({filter.name: {"$gte": value}})
        if filter.operator == "before":
            match.append({filter.name: {"$lt": value}})
        if filter.operator == "beforeOrOn":
            match.append({filter.name: {"$lte": value}})
        if filter.operator == "inrange" and isinstance(value, list):
            match.append({filter.name: {"$gte": value[0], "$lte": value[1]}})
        if filter.operator == "notinrange" and isinstance(value, list):
            match.append(
                {
                    "$or": [
                        {filter.name: {"$gt": value[1]}},
                        {filter.name: {"$lt": value[0]}},
                    ]
                }
            )

    sort_by = [(s.name, s.dir) for s in sorts if s.dir]
    [print(m) for m in match]

    return (match, sort_by)


def construct_table_query(
    query: FindMany[T],  # type: ignore
    sorts: list[TableSortInfo] = [],
    filters: list[TableFilterInfo] = [],
) -> FindMany[T]:  # type: ignore
    (match_filter, sort_by) = _prepare_table_query(sorts, filters)
    for filter in match_filter:
        query = query.find(filter)
    for sort in sort_by:
        query = query.sort(sort)  # type: ignore
    return query


def query_as_agg(
    query: FindMany[T],
    limit: int | None = None,
    skip: int | None = None,
) -> AggregationQuery[dict[str, Any]]:
    agg_query: list = [
        {"$match": query.get_filter_query()},
    ]
    # Sort, skip, limit.
    if hasattr(query, "sort_expressions") and query.sort_expressions:
        agg_query.append({"$sort": {key: dir for key, dir in query.sort_expressions}})
    agg_query.append({"$skip": skip or 0})
    agg_query.append({"$limit": limit or 0})
    # Convert projection from find syntax to aggregation syntax.
    # 'find' projection slice operator, n is the only input.
    # 'aggregation' projection slice operator, ['$array', n] is the input.
    if hasattr(query, "projection_model") and query.projection_model:
        inclusion_projection = {}
        projection = get_projection(query.projection_model)
        for projection_key in projection:
            # Copy dict value to new object so that changes to projection_value does not
            # affect original projection (python dict value assign by ref).
            projection_value = copy.copy(projection[projection_key])
            # exclusion projection is any projection with value of 0.
            # Used in find to exclude fields, but query_as_agg explicitly includes.
            # Cannot mix inclusion projection with exclusion projection.
            if projection_value == 0:
                continue
            if isinstance(projection_value, dict):
                if "$slice" in projection_value:
                    projection_value["$slice"] = [f"${projection_key}", projection_value["$slice"]]
            inclusion_projection[projection_key] = projection_value
        agg_query.append({"$project": inclusion_projection})
    # Should almost always sort in memory, but in rare cases like search name
    # or link text for all docs, may exceed 100mb sort limit.
    # Disk sort needed - even with index.
    data = query.document_model.aggregate(aggregation_pipeline=agg_query, allowDiskUse=True)
    return data


async def query_table(
    query: FindMany[T],  # type: ignore
    limit: int | None = None,
    skip: int | None = None,
    sorts: list[TableSortInfo] = [],
    filters: list[TableFilterInfo] = [],
    as_aggregation: bool = False,
) -> TableQueryResponse[T]:
    query = construct_table_query(query, sorts, filters)

    if limit:
        query = query.limit(limit)
    if skip:
        query = query.skip(skip)

    data_q: AggregationQuery[dict[str, Any]] | FindMany[T] = (
        query_as_agg(query, limit, skip) if as_aggregation else query
    ).to_list()

    if query.find_expressions == [{}]:
        total_q = query.document_model.get_motor_collection().estimated_document_count()
    else:
        total_q = query.count()
    (data, total) = await asyncio.gather(data_q, total_q)
    if as_aggregation:
        data = [query.projection_model(**doc) for doc in data]

    return TableQueryResponse(data=data, total=total)
