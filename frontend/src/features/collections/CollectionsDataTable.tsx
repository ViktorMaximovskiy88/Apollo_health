import { useCallback, useMemo } from 'react';
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
} from './siteScrapeTasksApi';
import { createColumns } from './createColumns';
import { useDataTableSort } from '../../common/hooks/use-data-table-sort';
import { useDataTableFilter } from '../../common/hooks/use-data-table-filter';

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
  openNewDocumentModal:() => void;
}

export function CollectionsDataTable({ siteId, openErrorModal, openNewDocumentModal }: DataTablePropTypes) {
  const { data: scrapeTasks } = useGetScrapeTasksForSiteQuery(siteId, {
    pollingInterval: 3000,
    skip: !siteId,
  });

  const filterProps = useDataTableFilter(collectionTableState, setCollectionTableFilter);
  const sortProps = useDataTableSort(collectionTableState, setCollectionTableSort);
  const controlledPagination = useControlledPagination();

  const [cancelScrape, { isLoading: isCanceling }] = useCancelSiteScrapeTaskMutation();

  const columns = useMemo(
    () => createColumns({ cancelScrape, isCanceling, openErrorModal, openNewDocumentModal }),
    [cancelScrape, isCanceling, openErrorModal, openNewDocumentModal]
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
