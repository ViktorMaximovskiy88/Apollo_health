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
  setSiteDocDocumentTableForceUpdate,
} from './siteDocDocumentsSlice';
import { useDataTableSort, useDataTableFilter, useDataTablePagination } from '../../common/hooks';
import { useSiteDocDocumentColumns } from './useSiteDocDocumentColumns';
import { SiteDocDocument } from './types';
import { useInterval } from '../../common/hooks';
import { useDispatch, useSelector } from 'react-redux';
import {
  uniqueDocumentFamilyIds,
  useGetDocumentFamilyNamesById,
} from './document_family/documentFamilyHooks';
import { uniquePayerFamilyIds, useGetPayerFamilyNamesById } from '../payer-family/payerFamilyHooks';
import { Alert } from 'antd';
import { statusDisplayAndStyle } from '../../common/scrapeTaskStatus';
import { SiteScrapeTask } from '../collections/types';
import { prettyDateDistanceSingle, prettyDateTimeFromISO } from '../../common';
import { collectMethodDisplayName } from '../sites/types';
import classNames from 'classnames';

interface DataTablePropTypes {
  handleNewVersion: (data: SiteDocDocument) => void;
  siteScrapeTask: SiteScrapeTask | undefined;
  setSiteScrapeTask: (value: SiteScrapeTask | undefined) => void;
  scrapeTaskId: string | null;
  setScrapeTaskId: (value: string) => void;
}

export function SiteDocDocumentsTable({
  handleNewVersion,
  siteScrapeTask,
  setSiteScrapeTask,
  scrapeTaskId,
  setScrapeTaskId,
}: DataTablePropTypes) {
  const { siteId } = useParams();
  const { watermark } = useInterval(10000);
  const [getDocDocumentsQuery] = useLazyGetSiteDocDocumentsQuery();
  const [searchParams, setSearchParams] = useSearchParams();
  const { setDocumentFamilyIds, documentFamilyNamesById } = useGetDocumentFamilyNamesById();
  const { setPayerFamilyIds, payerFamilyNamesById } = useGetPayerFamilyNamesById();
  const dispatch = useDispatch();

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
    siteScrapeTask,
    setSiteScrapeTask,
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
    const statusLabel = statusDisplayAndStyle(siteScrapeTask.status);
    return statusLabel.name;
  }
  const dateLabel = prettyDateTimeFromISO(
    siteScrapeTask?.end_time || siteScrapeTask?.start_time || siteScrapeTask?.queued_time
  );
  function elapsedLable(siteScrapeTask: SiteScrapeTask) {
    if (!siteScrapeTask || !siteScrapeTask.start_time) {
      return '0 seconds';
    }
    const formattedDate = prettyDateDistanceSingle(
      siteScrapeTask.start_time || siteScrapeTask.queued_time,
      siteScrapeTask.end_time
    );
    if (!formattedDate) {
      return '0 seconds';
    }

    return formattedDate;
  }

  async function handleOnClose() {
    if (searchParams.has('scrape_task_id')) {
      searchParams.delete('scrape_task_id');
      setSearchParams(searchParams);
      setScrapeTaskId('');
      setSiteScrapeTask(undefined);
      dispatch(setSiteDocDocumentTableForceUpdate());
    }
  }

  return (
    <>
      {siteScrapeTask && (
        <Alert
          message={
            <div>
              <span className={classNames('mr-2 opacity-80')}>Filtered by Collection</span>|
              <span className={classNames('mx-2')}>
                {siteScrapeTaskStatusLabel(siteScrapeTask)} on {dateLabel}
              </span>
              |
              <span className={classNames('mx-2 opacity-80')}>
                {collectMethodDisplayName(siteScrapeTask?.collection_method)}
              </span>
              |<span className={classNames('mx-2 opacity-80')}>{elapsedLable(siteScrapeTask)}</span>
            </div>
          }
          type="success"
          className="mb-1"
          closable
          onClose={handleOnClose}
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
