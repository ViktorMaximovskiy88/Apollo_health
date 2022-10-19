import { useState } from 'react';
import { Button } from 'antd';
import { useParams } from 'react-router-dom';

import { MainLayout } from '../../components';
import { SiteMenu } from '../sites/SiteMenu';
import { ManualCollectionButton } from '../collections/CollectionsPage';
import { SiteStatus } from '../sites/siteStatus';
import { CollectionMethod } from '../sites/types';
import { SiteDocDocumentsTable } from './SiteDocDocumentsTable';
import { AddDocumentModal } from '../collections/AddDocumentModal';
import { SiteDocDocument } from './types';
import { useGetSiteQuery } from '../sites/sitesApi';
import { useRunSiteScrapeTaskMutation } from '../collections/siteScrapeTasksApi';

export function SiteDocDocumentsPage() {
  const [newDocumentModalOpen, setNewDocumentModalOpen] = useState(false);
  const [oldVersion, setOldVersion] = useState<any>();
  const { siteId } = useParams();
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

  return (
    <MainLayout
      sidebar={<SiteMenu />}
      sectionToolbar={
        <>
          {site.collection_method === CollectionMethod.Manual &&
          site.status !== SiteStatus.Inactive &&
          site.is_running_manual_collection ? (
            <ManualCollectionButton site={site} refetch={refetch} runScrape={runScrape} />
          ) : null}

          <Button onClick={() => setNewDocumentModalOpen(true)} className="ml-auto">
            Create Document
          </Button>
        </>
      }
    >
      {newDocumentModalOpen && (
        <AddDocumentModal oldVersion={oldVersion} setOpen={hideNewDocument} siteId={siteId} />
      )}
      <SiteDocDocumentsTable handleNewVersion={handleNewVersion} />
    </MainLayout>
  );
}
