import { useParams, useSearchParams } from 'react-router-dom';
import ReactDataGrid from '@inovua/reactdatagrid-community';
import { useGetSiteDocDocumentsQuery } from '../sites/sitesApi';
import {
  docDocumentTableState,
  setDocDocumentTableFilter,
  setDocDocumentTableLimit,
  setDocDocumentTableSkip,
  setDocDocumentTableSort,
} from './docDocumentsSlice';
import { useDataTableSort, useDataTableFilter, useDataTablePagination } from '../../common/hooks';
import { useSiteDocDocumentColumns } from './useSiteDocDocumentColumns';
import { SiteDocDocument } from './types';

interface DataTablePropTypes {
  handleNewVersion: (data: SiteDocDocument) => void;
}

export function SiteDocDocumentsTable({ handleNewVersion }: DataTablePropTypes) {
  const { siteId } = useParams();
  const [searchParams] = useSearchParams();
  const scrapeTaskId = searchParams.get('scrape_task_id');

  const { data } = useGetSiteDocDocumentsQuery({ siteId, scrapeTaskId }, { pollingInterval: 5000 });
  const documents = data ?? [];

  const columns = useSiteDocDocumentColumns({ handleNewVersion });
  const filterProps = useDataTableFilter(docDocumentTableState, setDocDocumentTableFilter);
  const sortProps = useDataTableSort(docDocumentTableState, setDocDocumentTableSort);
  const controlledPagination = useDataTablePagination(
    docDocumentTableState,
    setDocDocumentTableLimit,
    setDocDocumentTableSkip
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
