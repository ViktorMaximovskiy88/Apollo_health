import { useCallback, useState } from 'react';
import ReactDataGrid from '@inovua/reactdatagrid-community';
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
  useGetCollectionConfigQuery,
  useLazyGetScrapeTasksForSiteQuery,
} from './siteScrapeTasksApi';
import { useCollectionsColumns as useColumns } from './useCollectionsColumns';
import { TypeFilterValue, TypeSortInfo } from '@inovua/reactdatagrid-community/types';
import { useInterval } from '../../common/hooks';
import { TableInfoType } from '../../common/types';
import { SiteScrapeTask } from './types';
import { DateTime } from 'luxon';

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

export const useSiteScrapeFilter = (siteId: string, dateOffset: number | undefined) => {
  let { filter: filterValue }: { filter: TypeFilterValue } = useSelector(collectionTableState);

  filterValue = [
    {
      name: 'queued_time',
      operator: 'after',
      type: 'date',
      value: DateTime.now().minus({ days: dateOffset }).toLocaleString(DateTime.DATE_MED),
    },
    { name: 'status', operator: 'eq', type: 'select', value: null },
  ];

  const dispatch = useDispatch();
  const onFilterChange = useCallback(
    (filter: TypeFilterValue) => dispatch(setCollectionTableFilter(filter)),
    [dispatch]
  );

  const filterProps = {
    defaultFilterValue: filterValue,
    filterValue,
    onFilterValueChange: onFilterChange,
  };
  return filterProps;
};

export const useSiteScrapeSort = () => {
  const { sort: sortInfo }: { sort: TypeSortInfo } = useSelector(collectionTableState);
  const dispatch = useDispatch();
  const onSortChange = useCallback(
    (sortInfo: TypeSortInfo) => dispatch(setCollectionTableSort(sortInfo)),
    [dispatch]
  );
  const sortProps = {
    defaultSortInfo: sortInfo,
    sortInfo,
    onSortInfoChange: onSortChange,
  };
  return sortProps;
};

interface DataTablePropTypes {
  siteId: string;
  scrapeTasks?: { data: SiteScrapeTask[]; total: number };
  openNewDocumentModal: () => void;
}

export function CollectionsDataTable({ siteId, openNewDocumentModal }: DataTablePropTypes) {
  const [getCollectionsFn] = useLazyGetScrapeTasksForSiteQuery();
  const { watermark } = useInterval(5000);

  const loadData = useCallback(
    async (tableInfo: TableInfoType) => {
      const { data } = await getCollectionsFn({ ...tableInfo, siteId });
      const sites = data?.data ?? [];
      const count = data?.total ?? 0;
      return { data: sites, count };
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [getCollectionsFn, watermark]
  );

  const config = useGetCollectionConfigQuery('collections');
  const dateOffset = config.data?.data.defaultLastNDays;
  const filterProps = useSiteScrapeFilter(siteId, dateOffset);
  const sortProps = useSiteScrapeSort();
  const controlledPagination = useControlledPagination();

  const [cancelScrape, { isLoading: isCanceling }] = useCancelSiteScrapeTaskMutation();

  const openErrorModal = (errorTraceback: string): void => {
    setErrorTraceback(errorTraceback);
    setModalVisible(true);
  };

  const columns = useColumns({ cancelScrape, isCanceling, openErrorModal, openNewDocumentModal });

  const [modalVisible, setModalVisible] = useState(false);
  const [errorTraceback, setErrorTraceback] = useState('');

  return (
    <ReactDataGrid
      dataSource={loadData}
      {...filterProps}
      {...sortProps}
      {...controlledPagination}
      columns={columns}
      rowHeight={50}
    />
  );
}
