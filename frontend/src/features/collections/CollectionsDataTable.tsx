import { useCallback, useMemo } from 'react';
import ReactDataGrid from '@inovua/reactdatagrid-community';
import { TypeFilterValue, TypeSortInfo } from '@inovua/reactdatagrid-community/types';
import { useDispatch, useSelector } from 'react-redux';
import {
  collectionTableState,
  setCollectionTableFilter,
  setCollectionTableLimit,
  setCollectionTableSkip,
  setCollectionTableSort,
} from './collectionsSlice';
import {
  useCancelSiteScrapeTaskMutation,
  useGetScrapeTasksForSiteQuery,
} from './siteScrapeTasksApi';
import { createColumns } from './createColumns';

const useFilter = () => {
  const tableState = useSelector(collectionTableState);
  const dispatch = useDispatch();
  const onFilterChange = useCallback(
    (filter: TypeFilterValue) => dispatch(setCollectionTableFilter(filter)),
    [dispatch]
  );
  const filterProps = {
    defaultFilterValue: tableState.filter,
    onFilterValueChange: onFilterChange,
  };
  return filterProps;
};

const useSort = () => {
  const tableState = useSelector(collectionTableState);
  const dispatch = useDispatch();
  const onSortChange = useCallback(
    (sort: TypeSortInfo) => dispatch(setCollectionTableSort(sort)),
    [dispatch]
  );
  const sortProps = {
    defaultSortInfo: tableState.sort,
    onSortInfoChange: onSortChange,
  };
  return sortProps;
};

const useControlledPagination = () => {
  const tableState = useSelector(collectionTableState);
  const dispatch = useDispatch();

  const onLimitChange = useCallback(
    (limit: number) => dispatch(setCollectionTableLimit(limit)),
    [dispatch]
  );
  const onSkipChange = useCallback(
    (skip: number) => dispatch(setCollectionTableSkip(skip)),
    [dispatch]
  );
  const controlledPaginationProps = {
    pagination: true,
    limit: tableState.pagination.limit,
    onLimitChange,
    skip: tableState.pagination.skip,
    onSkipChange,
  };
  return controlledPaginationProps;
};

interface DataTablePropTypes {
  siteId: string;
  openErrorModal: (errorTraceback: string) => void;
}
export function CollectionsDataTable({ siteId, openErrorModal }: DataTablePropTypes) {
  const { data: scrapeTasks } = useGetScrapeTasksForSiteQuery(siteId, {
    pollingInterval: 3000,
    skip: !siteId,
  });

  const filterProps = useFilter();
  const sortProps = useSort();
  const controlledPagination = useControlledPagination();

  const [cancelScrape, { isLoading: isCanceling }] = useCancelSiteScrapeTaskMutation();

  const columns = useMemo(
    () => createColumns({ cancelScrape, isCanceling, openErrorModal }),
    [cancelScrape, isCanceling, openErrorModal]
  );

  return (
    <ReactDataGrid
      dataSource={scrapeTasks ?? []}
      {...filterProps}
      {...sortProps}
      {...controlledPagination}
      columns={columns}
      rowHeight={50}
    />
  );
}
