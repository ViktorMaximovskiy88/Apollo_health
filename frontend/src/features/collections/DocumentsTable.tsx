import { useParams, useSearchParams } from 'react-router-dom';
import { useGetDocumentsQuery } from '../retrieved_documents/documentsApi';
import { RetrievedDocument } from '../retrieved_documents/types';
import ReactDataGrid from '@inovua/reactdatagrid-community';
import { useCallback } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import {
  documentTableState,
  setDocumentTableFilter,
  setDocumentTableLimit,
  setDocumentTableSkip,
  setDocumentTableSort,
} from './documentsSlice';
import { useDataTableSort } from '../../common/hooks/use-data-table-sort';
import { useDataTableFilter } from '../../common/hooks/use-data-table-filter';
import { useDocumentColumns as useColumns } from './useDocumentColumns';

const useControlledPagination = () => {
  const tableState = useSelector(documentTableState);

  const dispatch = useDispatch();
  const onLimitChange = useCallback(
    (limit: number) => dispatch(setDocumentTableLimit(limit)),
    [dispatch]
  );
  const onSkipChange = useCallback(
    (skip: number) => dispatch(setDocumentTableSkip(skip)),
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

const useDocuments = (): RetrievedDocument[] => {
  const [searchParams] = useSearchParams();
  const params = useParams();
  const scrapeTaskId = searchParams.get('scrape_task_id');
  const siteId = params.siteId;
  const { data } = useGetDocumentsQuery(
    {
      scrape_task_id: scrapeTaskId,
      site_id: siteId,
    },
    { pollingInterval: 5000 }
  );
  const documents = data?.map((document) => ({
    ...document,
    link_text: document?.context_metadata?.link_text, // makes datatable filterable by link_text
  }));
  return documents ?? [];
};

export function DocumentsTable() {
  const documents = useDocuments();
  const columns = useColumns();

  const filterProps = useDataTableFilter(documentTableState, setDocumentTableFilter);
  const sortProps = useDataTableSort(documentTableState, setDocumentTableSort);
  const controlledPagination = useControlledPagination();

  return (
    <ReactDataGrid
      dataSource={documents}
      {...filterProps}
      {...sortProps}
      {...controlledPagination}
      rowHeight={50}
      columns={columns}
      columnUserSelect
    />
  );
}
