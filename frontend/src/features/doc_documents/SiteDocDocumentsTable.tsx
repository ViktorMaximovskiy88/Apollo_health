import { useCallback } from 'react';
import { useParams, useSearchParams } from 'react-router-dom';
import ReactDataGrid from '@inovua/reactdatagrid-community';
import { useLazyGetSiteDocDocumentsQuery, TableQueryInfo } from '../sites/sitesApi';
import { useDataTableSelection } from '../../common/hooks/use-data-table-select';
import {
  siteDocDocumentTableState,
  setSiteDocDocumentTableFilter,
  setSiteDocDocumentTableLimit,
  setSiteDocDocumentTableSkip,
  setSiteDocDocumentTableSort,
  setSiteDocDocumentTableSelect,
} from './siteDocDocumentsSlice';
import { useDataTableSort, useDataTableFilter, useDataTablePagination } from '../../common/hooks';
import { useSiteDocDocumentColumns } from './useSiteDocDocumentColumns';
import { SiteDocDocument } from './types';
import { useInterval } from '../../common/hooks';
import { useSelector } from 'react-redux';
import {
  uniqueDocumentFamilyIds,
  useGetDocumentFamilyNamesById,
} from './document_family/documentFamilyHooks';
import { uniquePayerFamilyIds, useGetPayerFamilyNamesById } from '../payer-family/payerFamilyHooks';
import { Alert } from 'antd';

interface DataTablePropTypes {
  handleNewVersion: (data: SiteDocDocument) => void;
}

export function SiteDocDocumentsTable({ handleNewVersion }: DataTablePropTypes) {
  const { siteId } = useParams();
  const [searchParams] = useSearchParams();
  const scrapeTaskId = searchParams.get('scrape_task_id');
  const { watermark } = useInterval(10000);
  const [getDocDocumentsQuery] = useLazyGetSiteDocDocumentsQuery();
  const { setDocumentFamilyIds, documentFamilyNamesById } = useGetDocumentFamilyNamesById();
  const { setPayerFamilyIds, payerFamilyNamesById } = useGetPayerFamilyNamesById();

  const { forceUpdate } = useSelector(siteDocDocumentTableState);
  const loadData = useCallback(
    async (tableParams: TableQueryInfo) => {
      const { data } = await getDocDocumentsQuery({ siteId, scrapeTaskId, ...tableParams });
      const docDocuments = data?.data ?? [];
      const count = data?.total ?? 0;
      if (docDocuments) {
        setDocumentFamilyIds(uniqueDocumentFamilyIds(docDocuments));
        setPayerFamilyIds(uniquePayerFamilyIds(docDocuments));
      }
      return { data: docDocuments, count };
    },
    [getDocDocumentsQuery, siteId, scrapeTaskId, setDocumentFamilyIds, watermark, forceUpdate] // eslint-disable-line react-hooks/exhaustive-deps
  );

  const columns = useSiteDocDocumentColumns({
    handleNewVersion,
    documentFamilyNamesById,
    payerFamilyNamesById,
  });
  const filterProps = useDataTableFilter(siteDocDocumentTableState, setSiteDocDocumentTableFilter);
  const sortProps = useDataTableSort(siteDocDocumentTableState, setSiteDocDocumentTableSort);
  const selectionProps = useDataTableSelection(
    siteDocDocumentTableState,
    setSiteDocDocumentTableSelect
  );
  const controlledPagination = useDataTablePagination(
    siteDocDocumentTableState,
    setSiteDocDocumentTableLimit,
    setSiteDocDocumentTableSkip
  );

  return (
    <>
      {scrapeTaskId ? (
        <Alert
          message={`Filtered by Site Scrape Task: ${scrapeTaskId}`}
          type="success"
          className="mb-1"
        />
      ) : (
        <Alert message="Showing All Documents" type="success" className="mb-1" />
      )}
      <ReactDataGrid
        idProperty="_id"
        dataSource={loadData}
        {...filterProps}
        {...sortProps}
        {...selectionProps}
        {...controlledPagination}
        rowHeight={50}
        columns={columns}
        renderLoadMask={() => <></>}
        columnUserSelect
        checkboxColumn
        checkboxOnlyRowSelect
        activateRowOnFocus={false}
      />
    </>
  );
}
