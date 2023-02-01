import {
  TypeFilterValue,
  TypeSingleFilterValue,
  TypeSortInfo,
} from '@inovua/reactdatagrid-community/types';

/*
 * Type predicate to narrow an unknown error to an object with status and data properties
 */
export function isErrorWithData(
  error: unknown
): error is { data: { detail: string }; status: number } {
  return (
    typeof error === 'object' &&
    error != null &&
    'data' in error &&
    typeof (error as any).data === 'object' &&
    typeof (error as any).data.detail === 'string' &&
    'status' in error &&
    typeof (error as any).status === 'number'
  );
}

export function makeActionDispatch(actions: object, dispatch: any) {
  const dispatchFunctions: { [key: string]: any } = {};
  for (const [name, func] of Object.entries(actions)) {
    dispatchFunctions[name] = (...args: any[]) => dispatch(func(...args));
  }
  return dispatchFunctions;
}

function valueExists(value: any) {
  return value === 0 || value;
}

function isActiveFilter(filter: TypeSingleFilterValue) {
  if (filter.operator.includes('range')) {
    return valueExists(filter.value.start) && valueExists(filter.value.end);
  }
  if (
    filter.operator === 'empty' ||
    filter.operator === 'notEmpty' ||
    filter.operator === 'notinlist' ||
    filter.operator === 'neq'
  )
    return true;

  return valueExists(filter.value);
}

export function makeTableFilters(
  filterValue?: TypeFilterValue,
  mapFunction: Function = (f: TypeSingleFilterValue) => f
) {
  return (filterValue || []).filter((f) => isActiveFilter(f)).map((f) => mapFunction(f));
}

export function makeTableSort(sortInfo: TypeSortInfo | undefined) {
  if (Array.isArray(sortInfo)) return sortInfo;
  return sortInfo ? [sortInfo] : [];
}

export function makeTableQueryParams(
  {
    limit,
    skip,
    sortInfo,
    filterValue,
  }: {
    limit?: number;
    skip?: number;
    sortInfo?: TypeSortInfo;
    filterValue?: TypeFilterValue;
  },
  additionalQueryParams: { [key: string]: any } = {},
  mapFunction?: Function
) {
  const sorts = makeTableSort(sortInfo);
  const filters = makeTableFilters(filterValue, mapFunction);
  const args = [];
  if (limit) args.push(`limit=${limit}`);
  if (skip) args.push(`skip=${skip}`);
  if (sorts) args.push(`sorts=${encodeURIComponent(JSON.stringify(sorts))}`);
  if (filters) args.push(`filters=${encodeURIComponent(JSON.stringify(filters))}`);

  const additionalArgs = Object.entries(additionalQueryParams)
    .filter(([_, v]) => v)
    .map(([key, value]) =>
      Array.isArray(value)
        ? `${key}=${encodeURIComponent(JSON.stringify(value))}`
        : `${key}=${encodeURIComponent(value)}`
    );
  return args.concat(additionalArgs);
}
