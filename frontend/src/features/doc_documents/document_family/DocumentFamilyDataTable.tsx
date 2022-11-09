import ReactDataGrid from '@inovua/reactdatagrid-community';
import { TypePaginationProps } from '@inovua/reactdatagrid-community/types';
import { useDocumentFamilyColumns as useColumns } from './useDocumentFamilyColumns';
import { useDataTableFilter, useDataTableSort, useInterval } from '../../../common/hooks';
import { useCallback } from 'react';
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
import { useLazyGetDocumentFamiliesQuery } from './documentFamilyApi';
import { useGetSiteNamesById } from '../DocDocumentsDataTable';
import { DocumentFamily } from './types';

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
  items.forEach((item) => (usedSiteIds[item.site_id] = true));
  return Object.keys(usedSiteIds);
}

export function DocumentFamilyTable() {
  const { isActive, setActive, watermark } = useInterval(10000);

  const [getDocumentFamiliesFn] = useLazyGetDocumentFamiliesQuery();
  const { setSiteIds, siteNamesById } = useGetSiteNamesById();

  const columns = useColumns(siteNamesById);
  const loadData = useCallback(
    async (tableInfo: TableInfoType) => {
      const { data } = await getDocumentFamiliesFn({ ...tableInfo });
      const families = data?.data ?? [];
      const count = data?.total ?? 0;
      if (families) setSiteIds(uniqueSiteIds(families));
      return { data: families, count };
    },
    [getDocumentFamiliesFn, watermark] // eslint-disable-line react-hooks/exhaustive-deps
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
    />
  );
}
