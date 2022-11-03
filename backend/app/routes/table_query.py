import asyncio
import json
from typing import Generic, TypeVar

from beanie import PydanticObjectId
from beanie.odm.queries.find import FindMany
from dateutil import parser
from fastapi import Request

from backend.common.models.base_document import BaseModel

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
    value: str | list[str] | None


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


def transform_value(filter_value: str, filter_type: str):
    if filter_type == "number":
        value = float(filter_value)
    elif filter_type == "date":
        value = parser.parse(filter_value)
    elif filter_type == "boolean":
        value = filter_value.lower() in ("true")
    else:
        value = filter_value

    try:
        value = PydanticObjectId(value)
    except Exception:
        pass

    return value


def construct_table_query(
    query: FindMany[T],  # type: ignore
    sorts: list[TableSortInfo] = [],
    filters: list[TableFilterInfo] = [],
) -> FindMany[T]:  # type: ignore
    for filter in filters:
        if not filter.value and filter.operator not in ["empty", "notEmpty"]:
            continue

        if not filter.value:
            filter.value = ""

        if isinstance(filter.value, list):
            value = [transform_value(value, filter.type) for value in filter.value]
        else:
            value = transform_value(filter.value, filter.type)

        if filter.operator == "contains":
            query = query.find({filter.name: {"$regex": value, "$options": "i"}})
        if filter.operator == "notContains":
            query = query.find({filter.name: {"$not": {"$regex": value, "$options": "i"}}})
        if filter.operator == "startsWith":
            query = query.find({filter.name: {"$regex": f"^{value}", "$options": "i"}})
        if filter.operator == "endsWith":
            query = query.find({filter.name: {"$regex": f"{value}$", "$options": "i"}})
        if filter.operator == "eq":
            if isinstance(value, list):
                query = query.find({filter.name: {"$in": value}})
            else:
                query = query.find({filter.name: value})
        if filter.operator == "neq":
            if isinstance(value, list):
                query = query.find({filter.name: {"$nin": value}})
            else:
                query = query.find({filter.name: {"$ne": value}})
        if filter.operator == "empty":
            query = query.find({filter.name: {"$in": [None, ""]}})
        if filter.operator == "notEmpty":
            query = query.find({filter.name: {"$exists": True, "$nin": [None, ""]}})
        if filter.operator in ["gt", "gte", "lt", "lte"]:
            query = query.find({filter.name: {f"${filter.operator}": value}})
        if filter.operator == "after":
            query = query.find({filter.name: {"$gt": value}})
        if filter.operator == "afterOrOn":
            query = query.find({filter.name: {"$gte": value}})
        if filter.operator == "before":
            query = query.find({filter.name: {"$lt": value}})
        if filter.operator == "beforeOrOn":
            query = query.find({filter.name: {"$lte": value}})

    for sort in sorts:
        if sort.dir == -1:
            query = query.sort(f"-{sort.name}")
        elif sort.dir == 1:
            query = query.sort(sort.name)
        # dir could be 0, in which case do not add sort

    return query


async def query_table(
    query: FindMany[T],  # type: ignore
    limit: int | None = None,
    skip: int | None = None,
    sorts: list[TableSortInfo] = [],
    filters: list[TableFilterInfo] = [],
) -> TableQueryResponse[T]:
    query = construct_table_query(query, sorts, filters)

    if limit:
        query = query.limit(limit)
    if skip:
        query = query.skip(skip)

    data_q = query.to_list()
    if query.find_expressions == [{}]:
        total_q = query.document_model.get_motor_collection().estimated_document_count()
    else:
        total_q = query.count()

    (data, total) = await asyncio.gather(data_q, total_q)

    return TableQueryResponse(data=data, total=total)
