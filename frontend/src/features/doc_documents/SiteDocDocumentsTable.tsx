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
import { useGetScrapeTaskQuery } from '../collections/siteScrapeTasksApi';
import { TaskStatus } from '../../common/scrapeTaskStatus';
import { SiteScrapeTask } from '../collections/types';
import { prettyDateDistanceSingle, prettyDateTimeFromISO } from '../../common';

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
  const { data: siteScrapeTask } = useGetScrapeTaskQuery(scrapeTaskId);

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

  function siteScrapeTaskStatusLabel(siteScrapeTask: SiteScrapeTask) {
    if (siteScrapeTask.status === TaskStatus.Queued) {
      return 'Queued';
    } else if (siteScrapeTask.status === TaskStatus.Pending) {
      return 'Pending';
    } else if (siteScrapeTask.status === TaskStatus.InProgress) {
      return 'Started';
    } else if (siteScrapeTask.status === TaskStatus.Failed) {
      return 'Failed';
    } else if (siteScrapeTask.status === TaskStatus.Canceling) {
      return 'Canceling';
    } else if (siteScrapeTask.status === TaskStatus.Canceled) {
      return 'Canceled';
    } else {
      return 'Finished';
    }
  }
  const dateLabel = prettyDateTimeFromISO(siteScrapeTask?.start_time);
  function collectionMethodLabel(siteScrapeTask: SiteScrapeTask) {
    if (siteScrapeTask?.collection_method === 'MANUAL') {
      return 'Manual Collection';
    } else {
      return 'Automated Collection';
    }
  }
  function elapsedLable(siteScrapeTask: SiteScrapeTask) {
    if (siteScrapeTask && siteScrapeTask.start_time) {
      return prettyDateDistanceSingle(siteScrapeTask.start_time, siteScrapeTask.end_time);
    } else {
      return '0 seconds';
    }
  }
  const collectionCount = siteScrapeTask?.retrieved_document_ids.length;
  function collectionCountLabel(siteScrapeTask: SiteScrapeTask) {
    if (siteScrapeTask.status === TaskStatus.InProgress) {
      return `Collecting ${collectionCount} Documents`;
    } else {
      return `${collectionCount} Documents Collected`;
    }
  }

  return (
    <>
      {siteScrapeTask && (
        <Alert
          message={
            <div>
              <span className="table-data-alert">{siteScrapeTaskStatusLabel(siteScrapeTask)}</span>|
              <span className="table-data-alert">
                {collectionCountLabel(siteScrapeTask)} on {dateLabel}
              </span>
              |
              <span className="table-data-alert-subheader">
                {collectionMethodLabel(siteScrapeTask)}
              </span>
              |<span className="table-data-alert-subheader">{elapsedLable(siteScrapeTask)}</span>
            </div>
          }
          type="success"
          className="mb-1"
        />
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
