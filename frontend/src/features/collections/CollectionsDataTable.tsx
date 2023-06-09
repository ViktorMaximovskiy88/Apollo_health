import { ReactNode, useCallback, useState } from 'react';
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
import { DateTime } from 'luxon';
import { useEffect } from 'react';
import { ErrorLogModal } from './ErrorLogModal';
import { Site } from '../sites/types';

function disableLoadingMask(data: {
  visible: boolean;
  livePagination: boolean;
  loadingText: ReactNode | (() => ReactNode);
  zIndex: number;
}) {
  return <></>;
}

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

export const useSiteScrapeFilter = (dateOffset?: number) => {
  let { filter: filterValue }: { filter: TypeFilterValue } = useSelector(collectionTableState);
  const dispatch = useDispatch();

  useEffect(() => {
    const defaultFilterValue = [
      {
        name: 'queued_time',
        operator: 'after',
        type: 'date',
        value: DateTime.utc().minus({ days: dateOffset }).toISODate(),
      },
      { name: 'status', operator: 'eq', type: 'select', value: null },
    ];
    dispatch(setCollectionTableFilter(defaultFilterValue));
  }, [dateOffset, dispatch]);

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
  site: Site;
  openNewDocumentModal: () => void;
}

export function CollectionsDataTable({ site, openNewDocumentModal }: DataTablePropTypes) {
  const [getCollectionsFn] = useLazyGetScrapeTasksForSiteQuery();
  const { watermark } = useInterval(5000);
  const siteId = site._id;

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

  const config = useGetCollectionConfigQuery();
  const dateOffset = config.data?.data.defaultLastNDays;
  const filterProps = useSiteScrapeFilter(dateOffset);

  const sortProps = useSiteScrapeSort();
  const controlledPagination = useControlledPagination();

  const [cancelScrape, { isLoading: isCanceling }] = useCancelSiteScrapeTaskMutation();

  const openErrorModal = (errorTraceback: string): void => {
    setErrorTraceback(errorTraceback);
    setModalOpen(true);
  };

  const columns = useColumns({
    cancelScrape,
    isCanceling,
    openErrorModal,
    openNewDocumentModal,
    site,
  });

  const [modalOpen, setModalOpen] = useState(false);
  const [errorTraceback, setErrorTraceback] = useState('');

  return (
    <>
      <ErrorLogModal open={modalOpen} setOpen={setModalOpen} errorTraceback={errorTraceback} />
      <ReactDataGrid
        dataSource={loadData}
        {...filterProps}
        {...sortProps}
        {...controlledPagination}
        columns={columns}
        renderLoadMask={disableLoadingMask}
        rowHeight={50}
        columnUserSelect
      />
    </>
  );
}
