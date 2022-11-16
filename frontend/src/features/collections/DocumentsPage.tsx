import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { Button } from 'antd';

import { MainLayout } from '../../components';
import { DocumentsTable } from './DocumentsTable';
import { AddDocumentModal } from './AddDocumentModal';
import { SiteMenu } from '../sites/SiteMenu';
import { useGetSiteQuery } from '../sites/sitesApi';
import { CollectionMethod } from '../sites/types';
import { TaskStatus } from '../../common/scrapeTaskStatus';

export function DocumentsPage() {
  const { siteId } = useParams();
  if (!siteId) return null;
  const { data: site, refetch } = useGetSiteQuery(siteId);
  if (!site) return null;
  const [newDocumentModalVisible, setNewDocumentModalVisible] = useState(false);
  const activeStatuses = [TaskStatus.Queued, TaskStatus.Pending, TaskStatus.InProgress];

  return (
    <MainLayout
      sidebar={<SiteMenu />}
      sectionToolbar={
        <>
          {site.collection_method === CollectionMethod.Manual &&
          activeStatuses.includes(site.last_run_status) ? (
            <Button onClick={() => setNewDocumentModalVisible(true)} className="ml-auto">
              Create Document
            </Button>
          ) : null}
        </>
      }
    >
      <DocumentsTable />
      {newDocumentModalVisible && (
        <AddDocumentModal setOpen={setNewDocumentModalVisible} siteId={siteId} />
      )}
    </MainLayout>
  );
}
