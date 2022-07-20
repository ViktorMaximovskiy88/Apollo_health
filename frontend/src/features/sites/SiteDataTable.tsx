import ReactDataGrid from '@inovua/reactdatagrid-community';
import { ReactNode, useCallback, useMemo, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  setSiteTableFilter,
  setSiteTableSort,
  setSiteTableLimit,
  setSiteTableSkip,
  siteTableState,
} from './sitesSlice';
import { GridPaginationToolbar } from '../../components';
import { useDeleteSiteMutation, useLazyGetSitesQuery } from './sitesApi';
import { useInterval } from '../../common/hooks';
import {
  TypeFilterValue,
  TypePaginationProps,
  TypeSortInfo,
} from '@inovua/reactdatagrid-community/types';
import { createColumns } from './createColumns';
import { useDataTableSort } from '../../common/hooks/use-data-table-sort';
import { useDataTableFilter } from '../../common/hooks/use-data-table-filter';

function disableLoadingMask(data: {
  visible: boolean;
  livePagination: boolean;
  loadingText: ReactNode | (() => ReactNode);
  zIndex: number;
}) {
  return <></>;
}

const useControlledPagination = ({
  isActive,
  setActive,
}: {
  isActive: boolean;
  setActive: (active: boolean) => void;
}) => {
  const tableState = useSelector(siteTableState);

  const dispatch = useDispatch();
  const onLimitChange = useCallback(
    (limit: number) => dispatch(setSiteTableLimit(limit)),
    [dispatch]
  );
  const onSkipChange = useCallback((skip: number) => dispatch(setSiteTableSkip(skip)), [dispatch]);

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

interface SiteDataTablePropTypes {
  setLoading: (loading: boolean) => void;
}
export function SiteDataTable({ setLoading }: SiteDataTablePropTypes) {
  // Trigger update every 10 seconds by invalidating memoized callback
  const { isActive, setActive, watermark } = useInterval(10000);

  const [getSitesFn] = useLazyGetSitesQuery();

  const [deletedSite, setDeletedSite] = useState('');
  interface TableInfoType {
    limit: number;
    skip: number;
    sortInfo: TypeSortInfo;
    filterValue: TypeFilterValue;
  }
  const loadData = useCallback(
    async (tableInfo: TableInfoType) => {
      setLoading(true);
      const { data } = await getSitesFn(tableInfo);
      setLoading(false);
      const sites = data?.data ?? [];
      const count = data?.total ?? 0;
      return { data: sites, count };
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [getSitesFn, watermark, setLoading, deletedSite] // watermark is not inside useCallback
  );

  const [deleteSite] = useDeleteSiteMutation();
  const columns = useMemo(
    () => createColumns(deleteSite, setDeletedSite),
    [deleteSite, setDeletedSite]
  );

  const filterProps = useDataTableFilter(siteTableState, setSiteTableFilter);
  const sortProps = useDataTableSort(siteTableState, setSiteTableSort);
  const controlledPagination = useControlledPagination({ isActive, setActive });

  return (
    <ReactDataGrid
      dataSource={loadData}
      {...filterProps}
      {...sortProps}
      {...controlledPagination}
      columns={columns}
      rowHeight={50}
      renderLoadMask={disableLoadingMask}
      activateRowOnFocus={false}
    />
  );
}
