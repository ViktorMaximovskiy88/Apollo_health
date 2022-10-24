import { TypePaginationProps } from '@inovua/reactdatagrid-community/types';
import { useCallback } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { GridPaginationToolbar } from '../../components';

export const useDataTablePagination = (
  tableStateSelector: any,
  setLimit: (limit: number) => void,
  setSkip: (skip: number) => void,
  autoActive?:
    | {
        isActive: boolean;
        setActive: (active: boolean) => void;
      }
    | undefined
) => {
  const { pagination }: { pagination: { limit: number; skip: number } } =
    useSelector(tableStateSelector);
  const dispatch = useDispatch();

  const onLimitChange = useCallback(
    (limit: number) => dispatch(setLimit(limit)),
    [dispatch, setLimit]
  );
  const onSkipChange = useCallback((skip: number) => dispatch(setSkip(skip)), [dispatch, setSkip]);

  const renderPaginationToolbar = useCallback(
    (paginationProps: TypePaginationProps) => {
      if (!autoActive) return undefined;
      const { isActive, setActive } = autoActive;
      return (
        <GridPaginationToolbar
          paginationProps={{ ...paginationProps }}
          autoRefreshValue={isActive}
          autoRefreshClick={setActive}
        />
      );
    },
    [autoActive]
  );
  const controlledPaginationProps = {
    ...pagination,
    pagination: true,
    onLimitChange,
    onSkipChange,
    renderPaginationToolbar,
  };
  return controlledPaginationProps;
};
