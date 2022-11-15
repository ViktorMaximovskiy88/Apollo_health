import { useState } from 'react';
import { Button } from 'antd';
import { useParams } from 'react-router-dom';

import { MainLayout } from '../../components';
import { SiteMenu } from '../sites/SiteMenu';
import { ManualCollectionButton } from '../collections/CollectionsPage';
import { SiteDocDocumentsTable } from './SiteDocDocumentsTable';
import { AddDocumentModal } from '../collections/AddDocumentModal';
import { SiteDocDocument } from './types';
import { useGetSiteQuery, useLazyGetSiteDocDocumentsQuery } from '../sites/sitesApi';
import {
  useLazyGetScrapeTasksForSiteQuery,
  useRunSiteScrapeTaskMutation,
} from '../collections/siteScrapeTasksApi';
import { useSiteScrapeTaskId } from './manual_collection/useUpdateSelected';
import { initialState } from '../collections/collectionsSlice';
import { TaskStatus } from '../../common/scrapeTaskStatus';

export function SiteDocDocumentsPage() {
  const [newDocumentModalOpen, setNewDocumentModalOpen] = useState(false);
  const [oldVersion, setOldVersion] = useState<any>();
  const activeStatuses = [TaskStatus.Queued, TaskStatus.Pending, TaskStatus.InProgress];
  const { siteId } = useParams();
  const scrapeTaskId = useSiteScrapeTaskId();
  const [getScrapeTasksForSiteQuery] = useLazyGetScrapeTasksForSiteQuery();
  const [getDocDocumentsQuery] = useLazyGetSiteDocDocumentsQuery();
  const [runScrape] = useRunSiteScrapeTaskMutation();
  const { data: site, refetch } = useGetSiteQuery(siteId);
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
    await getScrapeTasksForSiteQuery({ ...mostRecentTask, siteId });
    await getDocDocumentsQuery({ siteId, scrapeTaskId });
  };

  return (
    <MainLayout
      sidebar={<SiteMenu />}
      sectionToolbar={
        <>
          {site.collection_method === 'MANUAL' && activeStatuses.includes(site.last_run_status) ? (
            <ManualCollectionButton site={site} refetch={refetch} runScrape={runScrape} />
          ) : null}

          {site.collection_method === 'MANUAL' && activeStatuses.includes(site.last_run_status) ? (
            <Button onClick={() => setNewDocumentModalOpen(true)} className="ml-auto">
              Create Document
            </Button>
          ) : null}
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
