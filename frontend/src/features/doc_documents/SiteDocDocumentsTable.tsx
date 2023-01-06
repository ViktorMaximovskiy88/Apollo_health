import { useCallback } from 'react';
import { useParams } from 'react-router-dom';
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
import { statusDisplayAndStyle, TaskStatus } from '../../common/scrapeTaskStatus';
import { SiteScrapeTask } from '../collections/types';
import { prettyDateDistanceSingle, prettyDateTimeFromISO } from '../../common';
import { collectMethodDisplayName } from '../sites/types';
import classNames from 'classnames';

interface DataTablePropTypes {
  handleNewVersion: (data: SiteDocDocument) => void;
  siteScrapeTask: SiteScrapeTask | undefined;
  setSiteScrapeTask: (value: SiteScrapeTask) => void;
}

export function SiteDocDocumentsTable({
  handleNewVersion,
  siteScrapeTask,
  setSiteScrapeTask,
}: DataTablePropTypes) {
  const { siteId } = useParams();
  const { watermark } = useInterval(10000);
  const [getDocDocumentsQuery] = useLazyGetSiteDocDocumentsQuery();
  const scrapeTaskId = siteScrapeTask?._id || null;
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
    siteScrapeTask?.start_time || siteScrapeTask?.queued_time
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

  return (
    <>
      {siteScrapeTask && (
        <Alert
          message={
            <div>
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
