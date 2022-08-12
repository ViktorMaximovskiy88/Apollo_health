import { useState } from 'react';
import { useParams, useSearchParams } from 'react-router-dom';
import { Button } from 'antd';
import { MainLayout } from '../../components';
import { SiteDocumentsTable } from '../collections/SiteDocumentsTable';
import { AddDocumentModal } from '../collections/addDocumentModal';

import { SiteMenu } from '../sites/SiteMenu';
import { useGetSiteQuery } from '../sites/sitesApi';
import { CollectionMethod } from '../sites/types';

export function SiteRetreivedDocumentsPage() {
  const params = useParams();
  const [newDocumentModalVisible, setNewDocumentModalVisible] = useState(false);
  const { data: site } = useGetSiteQuery(params.siteId);
  return (
    <MainLayout
      sidebar={<SiteMenu />}
      pageTitle={'Retrieved Documents'}
      pageToolbar={
        site &&
        site.collection_method === CollectionMethod.Manual && (
          <Button onClick={() => setNewDocumentModalVisible(true)} className="ml-auto">
            Create Document
          </Button>
        )
      }
    >
      <SiteDocumentsTable />
      {newDocumentModalVisible ? (
        <AddDocumentModal setVisible={setNewDocumentModalVisible} siteId={params.siteId} />
      ) : null}
    </MainLayout>
  );
}
