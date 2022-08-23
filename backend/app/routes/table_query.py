import json
from typing import Generic, TypeVar

from beanie import PydanticObjectId
from beanie.odm.queries.find import FindMany
from dateutil import parser
from fastapi import Request
from pydantic import BaseModel

# Ideally this would be bound to BaseDocument, but beanie type inference
# chokes when attempting to identify collection
T = TypeVar("T")


class TableSortInfo(BaseModel):
    name: str
    dir: int


class TableFilterInfo(BaseModel):
    name: str
    operator: str
    type: str
    value: str | None


class TableQueryResponse(BaseModel, Generic[T]):
    data: list[T]
    total: int


def get_query_json_list(arg: str, type):
    def func(request: Request):
        value_str = request.query_params.get(arg, None)
        if value_str:
            values: list[type] = json.loads(value_str)
            return [type.parse_obj(v) for v in values]
        else:
            return []

    return func


#  reuse for aggregates and find
def build_match(
    filters: list[TableFilterInfo] = [],
):
    match = {}
    for filter in filters:
        if not filter.value and filter.operator not in ["empty", "notEmpty"]:
            continue

        if not filter.value:
            filter.value = ""

        if filter.type == "number":
            value = float(filter.value)
        elif filter.type == "date":
            value = parser.parse(filter.value)
        else:
            value = filter.value

        try:
            value = PydanticObjectId(value)
        except Exception:
            pass

        if filter.operator == "contains":
            match[filter.name] = {"$regex": value, "$options": "i"}
        if filter.operator == "notContains":
            match[filter.name] = {"$not": {"$regex": value, "$options": "i"}}
        if filter.operator == "startsWith":
            match[filter.name] = {"$regex": f"^{value}", "$options": "i"}
        if filter.operator == "endsWith":
            match[filter.name] = {"$regex": f"{value}$", "$options": "i"}
        if filter.operator == "eq":
            match[filter.name] = value
        if filter.operator == "neq":
            match[filter.name] = {"$ne": value}
        if filter.operator == "empty":
            match[filter.name] = None
        if filter.operator == "notEmpty":
            match[filter.name] = {"$exists": True, "$ne": None}
        if filter.operator in ["gt", "gte", "lt", "lte"]:
            match[filter.name] = {f"${filter.operator}": value}
        if filter.operator == "after":
            match[filter.name] = {"$gt": value}
        if filter.operator == "afterOrOn":
            match[filter.name] = {"$gte": value}
        if filter.operator == "before":
            match[filter.name] = {"$lt": value}
        if filter.operator == "beforeOrOn":
            match[filter.name] = {"$lte": value}

    return match if len(match) > 0 else None


#  reuse for aggregates and find
def build_sort(
    sorts: list[TableSortInfo] = [],
):
    sorted = {}
    for sort in sorts:
        # dir could be 0, in which case do not add sort
        if sort.dir != 0:
            sorted[sort.name] = sort.dir

    return sorted if len(sorted) > 0 else None


#  helper for the query
def query_match(query: FindMany[T], match):
    for item in match:
        query = query.find(item)
    return query


#  helper for the sort
def query_order(query: FindMany[T], sort):
    for item in sort:
        query = query.sort(item)
    return query


async def query_table(
    query: FindMany[T],  # type: ignore
    limit: int | None = None,
    skip: int | None = None,
    sorts: list[TableSortInfo] = [],
    filters: list[TableFilterInfo] = [],
) -> TableQueryResponse[T]:

    match = build_match(filters)

    if match:
        query = query_match(query, match)

    total = await query.count()
    sort = build_sort(sorts)

    if sort:
        query = query_order(query, sort)

    if limit:
        query = query.limit(limit)
    if skip:
        query = query.skip(skip)

    data = await query.to_list()
    return TableQueryResponse(data=data, total=total)
