import { useCallback } from 'react';
import { useParams, useSearchParams } from 'react-router-dom';
import ReactDataGrid from '@inovua/reactdatagrid-community';
import { useLazyGetSiteDocDocumentsQuery, TableQueryInfo } from '../sites/sitesApi';
import {
  siteDocDocumentTableState,
  setSiteDocDocumentTableFilter,
  setSiteDocDocumentTableLimit,
  setSiteDocDocumentTableSkip,
  setSiteDocDocumentTableSort,
} from './siteDocDocumentsSlice';
import { useDataTableSort, useDataTableFilter, useDataTablePagination } from '../../common/hooks';
import { useSiteDocDocumentColumns } from './useSiteDocDocumentColumns';
import { SiteDocDocument } from './types';
import { useInterval } from '../../common/hooks';

interface DataTablePropTypes {
  handleNewVersion: (data: SiteDocDocument) => void;
}

export function SiteDocDocumentsTable({ handleNewVersion }: DataTablePropTypes) {
  const { siteId } = useParams();
  const [searchParams] = useSearchParams();
  const scrapeTaskId = searchParams.get('scrape_task_id');
  const { watermark } = useInterval(10000);

  const [getDocDocumentsQuery] = useLazyGetSiteDocDocumentsQuery();

  const loadData = useCallback(
    async (tableParams: TableQueryInfo) => {
      const { data } = await getDocDocumentsQuery({ siteId, scrapeTaskId, ...tableParams });
      const sites = data?.data ?? [];
      const count = data?.total ?? 0;
      return { data: sites, count };
    },
    [getDocDocumentsQuery, watermark]
  );

  const columns = useSiteDocDocumentColumns({ handleNewVersion });
  const filterProps = useDataTableFilter(siteDocDocumentTableState, setSiteDocDocumentTableFilter);
  const sortProps = useDataTableSort(siteDocDocumentTableState, setSiteDocDocumentTableSort);
  const controlledPagination = useDataTablePagination(
    siteDocDocumentTableState,
    setSiteDocDocumentTableLimit,
    setSiteDocDocumentTableSkip
  );

  return (
    <ReactDataGrid
      dataSource={loadData}
      {...filterProps}
      {...sortProps}
      {...controlledPagination}
      rowHeight={50}
      columns={columns}
      renderLoadMask={() => <></>}
    />
  );
}
