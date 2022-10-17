import { useState, useEffect } from 'react';
import { Button } from 'antd';
import { useParams } from 'react-router-dom';
import { useLazyGetSiteDocDocumentsQuery } from '../sites/sitesApi';

import { MainLayout } from '../../components';
import { SiteMenu } from '../sites/SiteMenu';

import { SiteDocDocumentsTable } from './SiteDocDocumentsTable';
import { AddDocumentModal } from '../collections/AddDocumentModal';
import { SiteDocDocument } from './types';
import { useSiteScrapeTaskId } from '../doc_documents/manual_collection/useUpdateSelected';
import { useLazyGetScrapeTasksForSiteQuery } from '../collections/siteScrapeTasksApi';
import { initialState } from '../collections/collectionsSlice';

export function SiteDocDocumentsPage() {
  const [newDocumentModalOpen, setNewDocumentModalOpen] = useState(false);
  const [refreshSiteDocs, setRefreshSiteDocs] = useState(false);
  const [oldVersion, setOldVersion] = useState<any>();
  const { siteId } = useParams();
  const scrapeTaskId = useSiteScrapeTaskId();
  const [getScrapeTasksForSiteQuery] = useLazyGetScrapeTasksForSiteQuery();
  const [getDocDocumentsQuery] = useLazyGetSiteDocDocumentsQuery();

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

  useEffect(() => {
    if (refreshSiteDocs) {
      refreshDocs();
      setRefreshSiteDocs(false);
    }
  });

  return (
    <MainLayout
      sidebar={<SiteMenu />}
      sectionToolbar={
        <>
          <Button onClick={() => setNewDocumentModalOpen(true)} className="ml-auto">
            Create Document
          </Button>
        </>
      }
    >
      {newDocumentModalOpen && (
        <AddDocumentModal
          oldVersion={oldVersion}
          setOpen={hideNewDocument}
          siteId={siteId}
          setRefreshSiteDocs={setRefreshSiteDocs}
        />
      )}
      <SiteDocDocumentsTable handleNewVersion={handleNewVersion} />
    </MainLayout>
  );
}
