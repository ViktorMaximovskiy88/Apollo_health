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
  useGetScrapeTasksForSiteQuery,
  useLazyGetScrapeTasksForSiteQuery,
} from './siteScrapeTasksApi';
import { useCollectionsColumns as useColumns } from './useCollectionsColumns';
import { useDataTableSort } from '../../common/hooks/use-data-table-sort';
import { TypeFilterValue, TypeSortInfo } from '@inovua/reactdatagrid-community/types';
import {
  prettyDate,
  prettyDateDistance,
  prettyDateFromISO,
  prettyDateTimeFromISO,
  toDateTimeFromISO,
} from '../../common';
import { TableInfoType } from '../../common/types';

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

export const useSiteScrapeFilter = () => {
  const { filter: filterValue }: { filter: TypeFilterValue } = useSelector(collectionTableState);
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

// const useDataTableFilter = (siteId: string) => {
//   const scrapeTasks = data?.data;

//   const mostRecentTime = scrapeTasks?.[0].queued_time;

//   const newFilter: TypeFilterValue = [
//     {
//       name: 'queued_time',
//       operator: 'inrange',
//       type: 'date',
//       value: {
//         start: mostRecentTime,
//         end: prettyDateTimeFromISO(toDateTimeFromISO(mostRecentTime).minus({ days: 10 }).toISO()),
//       },
//     },
//   ];

//   const { filter: filterValue }: { filter: TypeFilterValue } = useSelector(collectionTableState);

//   const dispatch = useDispatch();
//   const onFilterChange = useCallback(
//     (filter: TypeFilterValue) => {
//       dispatch(setCollectionTableFilter(filter));
//     },
//     [dispatch]
//   );

//   const filterProps = {
//     defaultFilterValue: newFilter,
//     onFilterValueChange: onFilterChange,
//   };
//   return filterProps;
// };
interface DataTablePropTypes {
  siteId: string;
  scrapeTasks?: SiteScrapeTask[];
  openNewDocumentModal: () => void;
}

export function CollectionsDataTable({
  siteId,
  openErrorModal,
  openNewDocumentModal,
}: DataTablePropTypes) {
  const [getCollectionsFn] = useLazyGetScrapeTasksForSiteQuery();

  const loadData = useCallback(
    async (tableInfo: TableInfoType) => {
      //  setLoading(true);
      const { data } = await getCollectionsFn({ ...tableInfo, siteId });
      //  setLoading(false);
      const sites = data?.data ?? [];
      const count = data?.total ?? 0;
      return { data: sites, count };
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [getCollectionsFn]
  );

  const filterProps = useSiteScrapeFilter();
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
