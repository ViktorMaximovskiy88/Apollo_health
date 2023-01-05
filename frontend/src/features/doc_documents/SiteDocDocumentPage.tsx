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
  useLazyGetScrapeTaskQuery,
  useRunSiteScrapeTaskMutation,
} from '../collections/siteScrapeTasksApi';
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
  const [runScrape] = useRunSiteScrapeTaskMutation();
  const { data: site, refetch } = useGetSiteQuery(siteId);
  const { data: initialSiteScrapeTask } = useGetScrapeTaskQuery(scrapeTaskId);
  const [getScrapeTaskQuery] = useLazyGetScrapeTaskQuery();
  const [siteScrapeTask, setSiteScrapeTask] = useState(initialSiteScrapeTask);
  if (siteScrapeTask === undefined && initialSiteScrapeTask) {
    setSiteScrapeTask(initialSiteScrapeTask);
  }
  if (!site) return null;

  function handleNewVersion(data: SiteDocDocument) {
    setOldVersion(data);
    setNewDocumentModalOpen(true);
  }

  function hideNewDocument(type: boolean) {
    setNewDocumentModalOpen(false);
    setOldVersion(null);
  }

  const refreshDocs = async () => {
    if (!scrapeTaskId) return;
    // Refresh the sitescrape task so that we have up to date work_items.
    const { data: refreshedSiteScrapeTask } = await getScrapeTaskQuery(scrapeTaskId);
    setSiteScrapeTask(refreshedSiteScrapeTask);
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
            <ManualCollectionButton
              site={site}
              refetch={refetch}
              runScrape={runScrape}
              setSiteScrapeTask={setSiteScrapeTask}
            />
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
      <SiteDocDocumentsTable
        handleNewVersion={handleNewVersion}
        siteScrapeTask={siteScrapeTask}
        setSiteScrapeTask={setSiteScrapeTask}
      />
    </MainLayout>
  );
}
