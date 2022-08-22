import { useState } from 'react';
import { useParams, useSearchParams } from 'react-router-dom';
import { Button } from 'antd';
import { MainLayout } from '../../components';
import { DocumentsTable } from './DocumentsTable';
import { AddDocumentModal } from './addDocumentModal';

import { SiteMenu } from '../sites/SiteMenu';

export function DocumentsPage() {
  const params = useParams();
  const searchParams = useSearchParams();
  const [newDocumentModalVisible, setNewDocumentModalVisible] = useState(false);
  return (
    <MainLayout
      sidebar={<SiteMenu />}
      pageTitle={'Retrieved Documents'}
      pageToolbar={
        <>
          <Button onClick={() => setNewDocumentModalVisible(true)} className="ml-auto">
            Create Document
          </Button>
        </>
      }
    >
      <DocumentsTable />
      {newDocumentModalVisible ? (
        <AddDocumentModal setVisible={setNewDocumentModalVisible} siteId={params.siteId} />
      ) : null}
    </MainLayout>
  );
}
