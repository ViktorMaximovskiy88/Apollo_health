import { useState } from 'react';
import { useParams, useSearchParams } from 'react-router-dom';
import { Button } from 'antd';
import { MainLayout } from '../../components';
import { DocumentsTable } from './DocumentsTable';
import { AddDocumentModal } from './addDocumentModal';

import { SiteMenu } from '../sites/SiteMenu';
import { useGetSiteQuery } from '../sites/sitesApi';
import { CollectionMethod } from '../sites/types';

export function DocumentsPage() {
  const params = useParams();
  const searchParams = useSearchParams();
  const [newDocumentModalVisible, setNewDocumentModalVisible] = useState(false);
  const { data: site } = useGetSiteQuery(params.siteId);
  return (
    <MainLayout
      sidebar={<SiteMenu />}
      pageTitle={'Retrieved Documents'}
      pageToolbar={
        site && site.collection_method === CollectionMethod.Manual ? (
          <Button onClick={() => setNewDocumentModalVisible(true)} className="ml-auto">
            Create Document
          </Button>
        ) : null
      }
    >
      <DocumentsTable />
      {newDocumentModalVisible ? (
        <AddDocumentModal setVisible={setNewDocumentModalVisible} siteId={params.siteId} />
      ) : null}
    </MainLayout>
  );
}
