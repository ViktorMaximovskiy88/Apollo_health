import { useCallback } from 'react';
import { useDispatch, useSelector } from 'react-redux';

export const useDataTablePagination = (
  tableStateSelector: any,
  setLimit: (limit: number) => void,
  setSkip: (skip: number) => void
) => {
  const { pagination }: { pagination: { limit: number; skip: number } } =
    useSelector(tableStateSelector);
  const dispatch = useDispatch();

  const onLimitChange = useCallback(
    (limit: number) => dispatch(setLimit(limit)),
    [dispatch, setLimit]
  );
  const onSkipChange = useCallback((skip: number) => dispatch(setSkip(skip)), [dispatch, setSkip]);
  const controlledPaginationProps = {
    pagination: true,
    limit: pagination.limit,
    onLimitChange,
    skip: pagination.skip,
    onSkipChange,
  };
  return controlledPaginationProps;
};
