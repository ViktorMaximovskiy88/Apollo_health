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
import { useDocumentColumns as useColumns } from './useDocumentColumns';

export function SiteDocumentsTable() {
  const { siteId } = useParams();
  const { data } = useGetSiteRetrievedDocumentsQuery(siteId, { pollingInterval: 5000 });

  const documents =
    data?.map((document) => ({
      ...document,
      link_text: document?.context_metadata?.link_text, // makes datatable filterable by link_text
    })) ?? [];

  const columns = useColumns();
  const filterProps = useDataTableFilter(documentTableState, setDocumentTableFilter);
  const sortProps = useDataTableSort(documentTableState, setDocumentTableSort);
  const controlledPagination = useDataTablePagination(
    documentTableState,
    setDocumentTableLimit,
    setDocumentTableSkip
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
