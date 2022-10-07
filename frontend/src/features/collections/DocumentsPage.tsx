import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { Button } from 'antd';
import { MainLayout } from '../../components';
import { DocumentsTable } from './DocumentsTable';
import { AddDocumentModal } from './AddDocumentModal';

import { SiteMenu } from '../sites/SiteMenu';

export function DocumentsPage() {
  const params = useParams();
  const [newDocumentModalVisible, setNewDocumentModalVisible] = useState(false);
  return (
    <MainLayout
      sidebar={<SiteMenu />}
      sectionToolbar={
        <>
          <Button onClick={() => setNewDocumentModalVisible(true)} className="ml-auto">
            Create Document
          </Button>
        </>
      }
    >
      <DocumentsTable />
      {newDocumentModalVisible && (
        <AddDocumentModal setVisible={setNewDocumentModalVisible} siteId={params.siteId} />
      )}
    </MainLayout>
  );
}
