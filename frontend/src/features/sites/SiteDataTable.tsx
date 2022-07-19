import ReactDataGrid from '@inovua/reactdatagrid-community';
import { ReactNode, useCallback, useMemo, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { setSiteTableFilter, setSiteTableSort, siteTableState } from '../../app/uiSlice';
import { GridPaginationToolbar } from '../../components';
import { useDeleteSiteMutation, useLazyGetSitesQuery } from './sitesApi';
import { useInterval } from '../../common/hooks';
import { TypeFilterValue, TypeSortInfo } from '@inovua/reactdatagrid-community/types';
import { createColumns } from './createColumns';

function disableLoadingMask(data: {
  visible: boolean;
  livePagination: boolean;
  loadingText: ReactNode | (() => ReactNode);
  zIndex: number;
}) {
  return <></>;
}

interface SiteDataTablePropTypes {
  setLoading: (loading: boolean) => void;
}
export function SiteDataTable({ setLoading }: SiteDataTablePropTypes) {
  const [deletedSite, setDeletedSite] = useState('');
  const tableState = useSelector(siteTableState);
  const [getSitesFn] = useLazyGetSitesQuery();
  const [deleteSite] = useDeleteSiteMutation();
  const columns = useMemo(
    () => createColumns(deleteSite, setDeletedSite),
    [deleteSite, setDeletedSite]
  );
  const dispatch = useDispatch();
  const onFilterChange = useCallback(
    (filter: TypeFilterValue) => dispatch(setSiteTableFilter(filter)),
    [dispatch]
  );
  const onSortChange = useCallback(
    (sort: TypeSortInfo) => dispatch(setSiteTableSort(sort)),
    [dispatch]
  );

  // Trigger update every 10 seconds by invalidating memoized callback
  const { setActive, isActive, watermark } = useInterval(10000);

  const loadData = useCallback(
    async (tableInfo: any) => {
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

  const renderPaginationToolbar = useCallback(
    (paginationProps: any) => {
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

  return (
    <ReactDataGrid
      dataSource={loadData}
      columns={columns}
      rowHeight={50}
      pagination
      defaultFilterValue={tableState.filter}
      filterValue={tableState.filter}
      onFilterValueChange={onFilterChange}
      defaultSortInfo={tableState.sort}
      onSortInfoChange={onSortChange}
      sortInfo={tableState.sort}
      renderLoadMask={disableLoadingMask}
      renderPaginationToolbar={renderPaginationToolbar}
      activateRowOnFocus={false}
    />
  );
}
