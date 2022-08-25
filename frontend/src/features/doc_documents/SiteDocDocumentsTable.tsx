import { useParams } from 'react-router-dom';
import ReactDataGrid from '@inovua/reactdatagrid-community';
import { useCallback } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { useGetSiteDocDocumentsQuery } from '../sites/sitesApi';
import {
  docDocumentTableState,
  setDocDocumentTableFilter,
  setDocDocumentTableLimit,
  setDocDocumentTableSkip,
  setDocDocumentTableSort,
} from './docDocumentsSlice';
import { useDataTableSort } from '../../common/hooks/use-data-table-sort';
import { useDataTableFilter } from '../../common/hooks/use-data-table-filter';
import { useSiteDocDocumentColumns } from './useSiteDocDocumentColumns';
import { SiteDocDocument } from './types';

const useControlledPagination = () => {
  const tableState = useSelector(docDocumentTableState);

  const dispatch = useDispatch();
  const onLimitChange = useCallback(
    (limit: number) => dispatch(setDocDocumentTableLimit(limit)),
    [dispatch]
  );
  const onSkipChange = useCallback(
    (skip: number) => dispatch(setDocDocumentTableSkip(skip)),
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

const useDocuments = (): SiteDocDocument[] => {
  const params = useParams();
  const siteId = params.siteId;
  const { data } = useGetSiteDocDocumentsQuery(siteId, { pollingInterval: 5000 });
  return data ?? [];
};

interface DataTablePropTypes {
  handleNewVersion: (data: SiteDocDocument) => void;
}

export function SiteDocDocumentsTable({ handleNewVersion }: DataTablePropTypes) {
  const documents = useDocuments();
  const columns = useSiteDocDocumentColumns({ handleNewVersion });

  const filterProps = useDataTableFilter(docDocumentTableState, setDocDocumentTableFilter);
  const sortProps = useDataTableSort(docDocumentTableState, setDocDocumentTableSort);
  const controlledPagination = useControlledPagination();

  return (
    <ReactDataGrid
      dataSource={documents}
      {...filterProps}
      {...sortProps}
      {...controlledPagination}
      rowHeight={50}
      columns={columns}
    />
  );
}
