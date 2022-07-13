import ReactDataGrid from '@inovua/reactdatagrid-community';
import { ReactNode, useCallback, useMemo } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { setSiteTableFilter, setSiteTableSort, siteTableState } from '../../app/uiSlice';
import { TaskStatus } from '../../common';
import { GridPaginationToolbar } from '../../components';
import { useDeleteSiteMutation, useLazyGetSitesQuery } from './sitesApi';
import { Site } from './types';
import { useInterval } from '../../common/hooks';
import { TypeFilterValue, TypeSortInfo } from '@inovua/reactdatagrid-community/types';
import { createColumns } from './createColumns';
import { DateTime } from 'luxon';

function isFailedLastSevenDays(site: Site) {
  if (site.last_run_status !== TaskStatus.Failed) {
    return false;
  }
  if (!site.last_run_time) {
    return false;
  }
  const lastRunTime = DateTime.fromISO(site.last_run_time);
  const sevenDaysAgo = DateTime.now().minus({ days: 7 });
  if (lastRunTime < sevenDaysAgo) {
    return false;
  }
  return true;
}

interface QuickFilterType {
  assignedToMe: boolean;
  unassigned: boolean;
  failedLastSevenDays: boolean;
}
export function executeQuickFilter(quickFilter: QuickFilterType) {
  return function (site: Site) {
    if (quickFilter.failedLastSevenDays && !isFailedLastSevenDays(site)) {
      return false;
    }
    // TODO: add assignedToMe and unassigned logic after roles are added
    return true;
  };
}

function disableLoadingMask(data: {
  visible: boolean;
  livePagination: boolean;
  loadingText: ReactNode | (() => ReactNode);
  zIndex: number;
}) {
  return <></>;
}

export function SiteDataTable() {
  const tableState = useSelector(siteTableState);
  const [getSitesFn] = useLazyGetSitesQuery();
  const [deleteSite] = useDeleteSiteMutation();
  const columns = useMemo(() => createColumns(deleteSite), [deleteSite]);
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
      const { data } = await getSitesFn(tableInfo);
      const { quickFilter } = tableState;
      let sites = data?.data ?? [];
      sites = sites.filter(executeQuickFilter(quickFilter));
      const count = sites.length;
      return { data: sites, count };
    },
    [getSitesFn, watermark, tableState]
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
      onFilterValueChange={onFilterChange}
      defaultSortInfo={tableState.sort}
      onSortInfoChange={onSortChange}
      renderLoadMask={disableLoadingMask}
      renderPaginationToolbar={renderPaginationToolbar}
      activateRowOnFocus={false}
    />
  );
}
