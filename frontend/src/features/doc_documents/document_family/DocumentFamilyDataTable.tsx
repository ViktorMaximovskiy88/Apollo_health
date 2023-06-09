import ReactDataGrid from '@inovua/reactdatagrid-community';
import { TypePaginationProps } from '@inovua/reactdatagrid-community/types';
import { useDocumentFamilyColumns as useColumns } from './useDocumentFamilyColumns';
import {
  useDataTableFilter,
  useDataTableSort,
  useInterval,
  useNotifyMutation,
} from '../../../common/hooks';
import { Dispatch, SetStateAction, useCallback, useEffect, useMemo, useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { GridPaginationToolbar } from '../../../components';
import {
  documentFamilyTableState,
  setDocumentFamilyFilter,
  setDocumentTableFamilyLimit,
  setDocumentFamilyTableSort,
  setDocumentFamilyTableSkip,
} from './documentFamilySlice';
import { TableInfoType } from '../../../common/types';
import { useGetSiteNamesById } from '../DocDocumentsDataTable';
import { DocumentFamily } from './types';
import {
  useDeleteDocumentFamilyMutation,
  useLazyGetDocumentFamiliesQuery,
} from './documentFamilyApi';

// prevents excessive rerenders
const useNotificationArgs = () => {
  const successArgs = useMemo(
    () => ({
      description: 'Document Family Edited Successfully.',
    }),
    []
  );
  const errorArgs = useMemo(
    () => ({
      description: 'An error occurred while updating the document family.',
    }),
    []
  );
  return { successArgs, errorArgs };
};

const useDeleteDocumentFamily = () => {
  const [deletedFamily, setDeletedFamily] = useState('');

  const [deleteDocumentFamily, deleteResult] = useDeleteDocumentFamilyMutation();

  useEffect(() => {
    if (deleteResult.isSuccess && deleteResult.originalArgs) {
      setDeletedFamily(deleteResult.originalArgs._id);
    }
  }, [deleteResult, setDeletedFamily]);

  const { successArgs, errorArgs } = useNotificationArgs();
  useNotifyMutation(deleteResult, successArgs, errorArgs);

  return { deletedFamily, deleteDocumentFamily };
};

const useControlledPagination = ({
  isActive,
  setActive,
}: {
  isActive: boolean;
  setActive: (active: boolean) => void;
}) => {
  const tableState = useSelector(documentFamilyTableState);
  const dispatch = useDispatch();

  const onLimitChange = useCallback(
    (limit: number) => dispatch(setDocumentTableFamilyLimit(limit)),
    [dispatch]
  );
  const onSkipChange = useCallback(
    (skip: number) => dispatch(setDocumentFamilyTableSkip(skip)),
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

function uniqueSiteIds(items: DocumentFamily[]) {
  const usedSiteIds: { [key: string]: boolean } = {};
  items.forEach((item) => item.site_ids.forEach((id) => (usedSiteIds[id] = true)));
  return Object.keys(usedSiteIds);
}

interface DocumentFamilyDataTableProps {
  setDocFamilyId: Dispatch<SetStateAction<string>>;
  setOpenEditDrawer: Dispatch<SetStateAction<boolean>>;
}

export function DocumentFamilyTable({
  setDocFamilyId,
  setOpenEditDrawer,
}: DocumentFamilyDataTableProps) {
  const { isActive, setActive, watermark } = useInterval(10000);

  const { deletedFamily, deleteDocumentFamily } = useDeleteDocumentFamily();

  const [getDocumentFamiliesFn] = useLazyGetDocumentFamiliesQuery();
  const { setSiteIds, siteNamesById } = useGetSiteNamesById();

  const columns = useColumns(
    siteNamesById,
    deleteDocumentFamily,
    setDocFamilyId,
    setOpenEditDrawer
  );
  const loadData = useCallback(
    async (tableInfo: TableInfoType) => {
      const { data } = await getDocumentFamiliesFn({ ...tableInfo });
      const families = data?.data ?? [];
      const count = data?.total ?? 0;
      if (families) setSiteIds(uniqueSiteIds(families));
      return { data: families, count };
    },
    [getDocumentFamiliesFn, watermark, deletedFamily] // eslint-disable-line react-hooks/exhaustive-deps
  );

  const filterProps = useDataTableFilter(documentFamilyTableState, setDocumentFamilyFilter);
  const sortProps = useDataTableSort(documentFamilyTableState, setDocumentFamilyTableSort);
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
