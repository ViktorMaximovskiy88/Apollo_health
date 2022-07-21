import { useCallback } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { TypeSortInfo } from '@inovua/reactdatagrid-community/types';

export const useDataTableSort = (
  tableStateSelector: any,
  setTableSort: (sortInfo: TypeSortInfo) => void
) => {
  const { sort: sortInfo }: { sort: TypeSortInfo } = useSelector(tableStateSelector);
  const dispatch = useDispatch();
  const onSortChange = useCallback(
    (sortInfo: TypeSortInfo) => dispatch(setTableSort(sortInfo)),
    [dispatch, setTableSort]
  );
  const sortProps = {
    defaultSortInfo: sortInfo,
    onSortInfoChange: onSortChange,
  };
  return sortProps;
};
