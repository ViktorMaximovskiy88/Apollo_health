import { useCallback, useMemo } from 'react';
import ReactDataGrid from '@inovua/reactdatagrid-community';
import {
  TypeFilterValue,
  TypeSortInfo,
} from '@inovua/reactdatagrid-community/types';
import { useDispatch, useSelector } from 'react-redux';
import {
  collectionTableState,
  setCollectionTableFilter,
  setCollectionTableSort,
} from '../../app/uiSlice';
import {
  useCancelSiteScrapeTaskMutation,
  useGetScrapeTasksForSiteQuery,
} from './siteScrapeTasksApi';
import { createColumns } from './createColumns';

interface DataTablePropTypes {
  siteId: string;
  openErrorModal: (errorTraceback: string) => void;
}

export function CollectionsDataTable({
  siteId,
  openErrorModal,
}: DataTablePropTypes) {
  const { data: scrapeTasks } = useGetScrapeTasksForSiteQuery(siteId, {
    pollingInterval: 3000,
    skip: !siteId,
  });
  const [cancelScrape, { isLoading: isCanceling }] =
    useCancelSiteScrapeTaskMutation();

  const columns = useMemo(
    () => createColumns({ cancelScrape, isCanceling, openErrorModal }),
    [cancelScrape, isCanceling, openErrorModal]
  );

  const tableState = useSelector(collectionTableState);
  const dispatch = useDispatch();
  const onFilterChange = useCallback(
    (filter: TypeFilterValue) => dispatch(setCollectionTableFilter(filter)),
    [dispatch]
  );
  const onSortChange = useCallback(
    (sort: TypeSortInfo) => dispatch(setCollectionTableSort(sort)),
    [dispatch]
  );

  return (
    <ReactDataGrid
      dataSource={scrapeTasks || []}
      columns={columns}
      rowHeight={50}
      defaultFilterValue={tableState.filter}
      onFilterValueChange={onFilterChange}
      defaultSortInfo={tableState.sort}
      onSortInfoChange={onSortChange}
    />
  );
}
