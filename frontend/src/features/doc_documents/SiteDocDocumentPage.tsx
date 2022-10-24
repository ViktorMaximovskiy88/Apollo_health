import { useState } from 'react';
import { Button } from 'antd';
import { useParams } from 'react-router-dom';

import { MainLayout } from '../../components';
import { SiteMenu } from '../sites/SiteMenu';
import { ManualCollectionButton } from '../collections/CollectionsPage';
import { CollectionMethod } from '../sites/types';
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

export function SiteDocDocumentsPage() {
  const [newDocumentModalOpen, setNewDocumentModalOpen] = useState(false);
  const [hasToggledShowManual, setHasToggledShowManual] = useState(false);
  const [showManual, setShowManual] = useState(false);
  const [oldVersion, setOldVersion] = useState<any>();
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
    setHasToggledShowManual(true);
    const lastTask = await getScrapeTasksForSiteQuery({ ...mostRecentTask, siteId });
    if (
      lastTask.data &&
      site.collection_method === CollectionMethod.Manual &&
      ['IN_PROGRESS', 'QUEUED', 'PENDING'].includes(lastTask.data?.data[0].status)
    ) {
      setShowManual(true);
    }
    await getDocDocumentsQuery({ siteId, scrapeTaskId });
  };

  if (site.collection_method === CollectionMethod.Manual && !hasToggledShowManual) {
    refreshDocs();
  }

  return (
    <MainLayout
      sidebar={<SiteMenu />}
      sectionToolbar={
        <>
          {showManual ? (
            <ManualCollectionButton site={site} refetch={refetch} runScrape={runScrape} />
          ) : null}

          {showManual ? (
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
