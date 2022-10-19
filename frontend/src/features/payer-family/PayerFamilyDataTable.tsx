import ReactDataGrid from '@inovua/reactdatagrid-community';
import { TypePaginationProps } from '@inovua/reactdatagrid-community/types';
import { usePayerFamilyColumns as useColumns } from './usePayerFamilyColumns';
import { useDataTableFilter, useDataTableSort, useInterval } from '../../common/hooks';
import { useCallback } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { GridPaginationToolbar } from '../../components';
import {
  payerFamilyTableState,
  setPayerFamilyFilter,
  setPayerTableFamilyLimit,
  setPayerFamilyTableSort,
  setPayerFamilyTableSkip,
} from './payerFamilySlice';
import { TableInfoType } from '../../common/types';
import { useLazyGetPayerFamiliesQuery } from './payerFamilyApi';

const useControlledPagination = ({
  isActive,
  setActive,
}: {
  isActive: boolean;
  setActive: (active: boolean) => void;
}) => {
  const tableState = useSelector(payerFamilyTableState);
  const dispatch = useDispatch();

  const onLimitChange = useCallback(
    (limit: number) => dispatch(setPayerTableFamilyLimit(limit)),
    [dispatch]
  );
  const onSkipChange = useCallback(
    (skip: number) => dispatch(setPayerFamilyTableSkip(skip)),
    [dispatch]
  );

  const renderPaginationToolbar = useCallback(
    (paginationProps: TypePaginationProps) => {
      return (
        <GridPaginationToolbar
          paginationProps={{ ...paginationProps }}
          autoRefreshValue={isActive}
          autoRefreshClick={setActive}
        />
      );
    },
    [isActive, setActive]
  );

  const controlledPaginationProps = {
    pagination: true,
    limit: tableState.pagination.limit,
    onLimitChange,
    skip: tableState.pagination.skip,
    onSkipChange,
    renderPaginationToolbar,
  };
  return controlledPaginationProps;
};

export function PayerFamilyTable() {
  const { isActive, setActive, watermark } = useInterval(10000);

  const columns = useColumns();
  const [getPayerFamiliesFn] = useLazyGetPayerFamiliesQuery();

  const loadData = useCallback(
    async (tableInfo: TableInfoType) => {
      const { data } = await getPayerFamiliesFn({ ...tableInfo });
      const families = data?.data ?? [];
      const count = data?.total ?? 0;
      return { data: families, count };
    },
    [getPayerFamiliesFn, watermark] // eslint-disable-line react-hooks/exhaustive-deps
  );

  const filterProps = useDataTableFilter(payerFamilyTableState, setPayerFamilyFilter);
  const sortProps = useDataTableSort(payerFamilyTableState, setPayerFamilyTableSort);
  const controlledPagination = useControlledPagination({ isActive, setActive });

  return (
    <ReactDataGrid
      dataSource={loadData}
      {...filterProps}
      {...sortProps}
      {...controlledPagination}
      columns={columns}
      rowHeight={50}
      renderLoadMask={() => <></>}
      activateRowOnFocus={false}
    />
  );
}
