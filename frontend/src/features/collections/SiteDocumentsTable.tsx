import { useParams, useSearchParams } from 'react-router-dom';
import { useGetSiteRetrievedDocumentsQuery } from '../sites/sitesApi';
import ReactDataGrid from '@inovua/reactdatagrid-community';
import {
  documentTableState,
  setDocumentTableFilter,
  setDocumentTableLimit,
  setDocumentTableSkip,
  setDocumentTableSort,
} from './documentsSlice';
import { useDataTableSort, useDataTableFilter, useDataTablePagination } from '../../common/hooks';
import { useDocumentColumns } from './useDocumentColumns';

export function SiteDocumentsTable() {
  const { siteId } = useParams();
  const [searchParams] = useSearchParams();
  const scrapeTaskId = searchParams.get('scrape_task_id');
  const { data } = useGetSiteRetrievedDocumentsQuery(
    { siteId, scrapeTaskId },
    { pollingInterval: 5000 }
  );

  // TODO belongs in the backend
  const documents =
    data?.map((document) => ({
      ...document,
      link_text: document?.context_metadata?.link_text, // makes datatable filterable by link_text
    })) ?? [];

  const columns = useDocumentColumns();
  const filterProps = useDataTableFilter(documentTableState, setDocumentTableFilter);
  const sortProps = useDataTableSort(documentTableState, setDocumentTableSort);
  const controlledPagination = useDataTablePagination(
    documentTableState,
    setDocumentTableLimit,
    setDocumentTableSkip,
    undefined
  );

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
