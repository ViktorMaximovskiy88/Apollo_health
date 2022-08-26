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
import { useCancelSiteScrapeTaskMutation } from './siteScrapeTasksApi';
import { useCollectionsColumns as useColumns } from './useCollectionsColumns';
import { useDataTableSort } from '../../common/hooks/use-data-table-sort';
import { useDataTableFilter } from '../../common/hooks/use-data-table-filter';
import { ErrorLogModal } from './ErrorLogModal';
import { SiteScrapeTask } from './types';

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
  scrapeTasks?: SiteScrapeTask[];
  openNewDocumentModal: () => void;
}

export function CollectionsDataTable({ scrapeTasks, openNewDocumentModal }: DataTablePropTypes) {
  const filterProps = useDataTableFilter(collectionTableState, setCollectionTableFilter);
  const sortProps = useDataTableSort(collectionTableState, setCollectionTableSort);
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
    <>
      <ErrorLogModal
        visible={modalVisible}
        setVisible={setModalVisible}
        errorTraceback={errorTraceback}
      />
      <ReactDataGrid
        dataSource={scrapeTasks ?? []}
        {...filterProps}
        {...sortProps}
        {...controlledPagination}
        columns={columns}
        rowHeight={50}
      />
    </>
  );
}
