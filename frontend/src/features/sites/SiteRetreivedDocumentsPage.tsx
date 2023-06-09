import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { Button } from 'antd';
import { MainLayout } from '../../components';
import { SiteDocumentsTable } from '../collections/SiteDocumentsTable';
import { AddDocumentModal } from '../collections/AddDocumentModal';

import { SiteMenu } from '../sites/SiteMenu';
import { useGetSiteQuery } from '../sites/sitesApi';
import { CollectionMethod } from '../sites/types';
import { TaskStatus } from '../../common/scrapeTaskStatus';

export function SiteRetreivedDocumentsPage() {
  const params = useParams();
  const [newDocumentModalOpen, setNewDocumentModalOpen] = useState(false);
  const { data: site } = useGetSiteQuery(params.siteId);
  const activeStatuses = [TaskStatus.Queued, TaskStatus.Pending, TaskStatus.InProgress];

  return (
    <MainLayout
      sidebar={<SiteMenu />}
      sectionToolbar={
        site &&
        site.collection_method === CollectionMethod.Manual &&
        activeStatuses.includes(site.last_run_status) && (
          <Button onClick={() => setNewDocumentModalOpen(true)}>Create Document</Button>
        )
      }
    >
      <SiteDocumentsTable />
      {newDocumentModalOpen && (
        <AddDocumentModal setOpen={setNewDocumentModalOpen} siteId={params.siteId} />
      )}
    </MainLayout>
  );
}
