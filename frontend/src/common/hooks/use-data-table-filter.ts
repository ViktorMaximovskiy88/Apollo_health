import { useCallback } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { TypeFilterValue } from '@inovua/reactdatagrid-community/types';

export const useDataTableFilter = (
  tableStateSelector: any,
  setTableFilter: (filterValue: TypeFilterValue) => void
) => {
  const { filter: filterValue }: { filter: TypeFilterValue } = useSelector(tableStateSelector);
  const dispatch = useDispatch();
  const onFilterChange = useCallback(
    (filter: TypeFilterValue) => dispatch(setTableFilter(filter)),
    [dispatch, setTableFilter]
  );
  const filterProps = {
    filterValue: filterValue,
    onFilterValueChange: onFilterChange,
  };
  return filterProps;
};
