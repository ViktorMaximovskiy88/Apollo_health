import ReactDataGrid from '@inovua/reactdatagrid-community';
import { TypePaginationProps } from '@inovua/reactdatagrid-community/types';
import { usePayerFamilyColumns as useColumns } from './usePayerFamilyColumns';
import {
  useDataTableFilter,
  useDataTableSort,
  useInterval,
  useNotifyMutation,
} from '../../common/hooks';
import { Dispatch, SetStateAction, useCallback, useEffect, useMemo, useState } from 'react';
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
import { useDeletePayerFamilyMutation, useLazyGetPayerFamiliesQuery } from './payerFamilyApi';

// prevents excessive rerenders
const useNotificationArgs = () => {
  const successArgs = useMemo(
    () => ({
      description: 'Payer Family Deleted Successfully.',
    }),
    []
  );
  const errorArgs = useMemo(
    () => ({
      description: 'An error occurred while updating the payer family.',
    }),
    []
  );
  return { successArgs, errorArgs };
};

const useDeletePayerFamily = () => {
  const [deletedFamily, setDeletedFamily] = useState('');

  const [deletePayerFamily, deleteResult] = useDeletePayerFamilyMutation();

  useEffect(() => {
    if (deleteResult.isSuccess && deleteResult.originalArgs) {
      setDeletedFamily(deleteResult.originalArgs._id);
    }
  }, [deleteResult, setDeletedFamily]);

  const { successArgs, errorArgs } = useNotificationArgs();
  useNotifyMutation(deleteResult, successArgs, errorArgs);

  return { deletedFamily, deletePayerFamily };
};

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

interface PayerFamilyDataTableProps {
  setPayerFamilyId: Dispatch<SetStateAction<string>>;
  setOpenEditDrawer: Dispatch<SetStateAction<boolean>>;
}

export function PayerFamilyTable({
  setOpenEditDrawer,
  setPayerFamilyId,
}: PayerFamilyDataTableProps) {
  const { isActive, setActive, watermark } = useInterval(10000);

  const { deletedFamily, deletePayerFamily } = useDeletePayerFamily();

  const columns = useColumns(setPayerFamilyId, setOpenEditDrawer, deletePayerFamily);
  const [getPayerFamiliesFn] = useLazyGetPayerFamiliesQuery();

  const loadData = useCallback(
    async (tableInfo: TableInfoType) => {
      const { data } = await getPayerFamiliesFn({ ...tableInfo });
      const families = data?.data ?? [];
      const count = data?.total ?? 0;
      return { data: families, count };
    },
    [getPayerFamiliesFn, watermark, deletedFamily] // eslint-disable-line react-hooks/exhaustive-deps
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
      columnUserSelect
    />
  );
}
