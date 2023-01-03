import { useCallback, useState } from 'react';
import { Button } from 'antd';
import { useParams, useSearchParams } from 'react-router-dom';

import { MainLayout } from '../../components';
import { SiteMenu } from '../sites/SiteMenu';
import { ManualCollectionButton } from '../collections/CollectionsPage';
import { SiteDocDocumentsTable } from './SiteDocDocumentsTable';
import { AddDocumentModal } from '../collections/AddDocumentModal';
import { SiteDocDocument } from './types';
import { useGetSiteQuery } from '../sites/sitesApi';
import {
  useGetScrapeTaskQuery,
  useLazyGetScrapeTasksForSiteQuery,
  useRunSiteScrapeTaskMutation,
} from '../collections/siteScrapeTasksApi';
import { initialState } from '../collections/collectionsSlice';
import { TaskStatus } from '../../common/scrapeTaskStatus';
import { DocTypeUpdateModal } from './DocTypeBulkUpdateModal';
import { useSelector } from 'react-redux';
import {
  setSiteDocDocumentTableForceUpdate,
  setSiteDocDocumentTableSelect,
  siteDocDocumentTableState,
} from './siteDocDocumentsSlice';
import { useAppDispatch } from '../../app/store';

function DocTypeUpdateModalToolbar() {
  const { siteId } = useParams();
  const tableState = useSelector(siteDocDocumentTableState);
  const dispatch = useAppDispatch();
  const onBulkSubmit = useCallback(() => {
    dispatch(setSiteDocDocumentTableForceUpdate());
    dispatch(setSiteDocDocumentTableSelect({ selected: {}, unselected: {} }));
  }, [dispatch, setSiteDocDocumentTableForceUpdate, setSiteDocDocumentTableSelect]);
  return (
    <DocTypeUpdateModal
      selection={tableState.selection}
      filterValue={tableState.filter}
      siteId={siteId}
      onBulkSubmit={onBulkSubmit}
    />
  );
}

export function SiteDocDocumentsPage() {
  const [newDocumentModalOpen, setNewDocumentModalOpen] = useState(false);
  const [oldVersion, setOldVersion] = useState<any>();
  const activeStatuses = [TaskStatus.Queued, TaskStatus.Pending, TaskStatus.InProgress];
  const { siteId } = useParams();
  const [searchParams] = useSearchParams();
  const scrapeTaskId = searchParams.get('scrape_task_id');
  const dispatch = useAppDispatch();
  const [getScrapeTasksForSiteQuery] = useLazyGetScrapeTasksForSiteQuery();
  const [runScrape] = useRunSiteScrapeTaskMutation();
  const { data: site, refetch } = useGetSiteQuery(siteId);
  const { data: siteScrapeTask } = useGetScrapeTaskQuery(scrapeTaskId);
  if (!site) return null;

  function handleNewVersion(data: SiteDocDocument) {
    setOldVersion(data);
    setNewDocumentModalOpen(true);
  }

  function hideNewDocument(type: boolean) {
    setNewDocumentModalOpen(false);
    setOldVersion(null);
  }

  const mostRecentTask = {
    limit: 1,
    skip: 0,
    sortInfo: initialState.table.sort,
    filterValue: initialState.table.filter,
  };
  const refreshDocs = async () => {
    if (!scrapeTaskId) return;
    // Get scrape tasks so we can match manual work_list items to docs.
    await getScrapeTasksForSiteQuery({ ...mostRecentTask, siteId });
    dispatch(setSiteDocDocumentTableForceUpdate());
  };

  return (
    <MainLayout
      sidebar={<SiteMenu />}
      sectionToolbar={
        <>
          {site.collection_method === 'MANUAL' &&
          siteScrapeTask?.collection_method === 'MANUAL' &&
          activeStatuses.includes(siteScrapeTask.status) ? (
            <ManualCollectionButton site={site} refetch={refetch} runScrape={runScrape} />
          ) : null}

          {site.collection_method === 'MANUAL' &&
          siteScrapeTask?.collection_method === 'MANUAL' &&
          activeStatuses.includes(siteScrapeTask.status) ? (
            <Button onClick={() => setNewDocumentModalOpen(true)} className="ml-auto">
              Create Document
            </Button>
          ) : null}
          {site.collection_method !== 'MANUAL' ? <DocTypeUpdateModalToolbar /> : null}
        </>
      }
    >
      {newDocumentModalOpen && (
        <AddDocumentModal
          oldVersion={oldVersion}
          setOpen={hideNewDocument}
          siteId={siteId}
          refetch={refreshDocs}
        />
      )}
      <SiteDocDocumentsTable handleNewVersion={handleNewVersion} />
    </MainLayout>
  );
}
