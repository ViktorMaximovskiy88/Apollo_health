import { useState } from 'react';
import { Button } from 'antd';
import { useParams } from 'react-router-dom';

import { MainLayout } from '../../components';
import { SiteMenu } from '../sites/SiteMenu';
import { DocDocumentsTable } from './DocDocumentsSiteTable';
import { AddDocumentModal } from '../collections/addDocumentModal';
import { DocDocument } from './types';

export function DocDocumentsPage() {
  const [newDocumentModalVisible, setNewDocumentModalVisible] = useState(false);
  const [oldVersion, setOldVersion] = useState<any>();
  const params = useParams();

  function handleNewVersion(data: DocDocument) {
    setOldVersion(data);
    setNewDocumentModalVisible(true);
  }

  function hideNewDocument(type: boolean) {
    setNewDocumentModalVisible(false);
    setOldVersion(null);
  }

  return (
    <MainLayout
      pageTitle={'Documents'}
      sidebar={<SiteMenu />}
      pageToolbar={
        <>
          <Button onClick={() => setNewDocumentModalVisible(true)} className="ml-auto">
            Create Document
          </Button>
        </>
      }
    >
      {newDocumentModalVisible && (
        <AddDocumentModal
          oldVersion={oldVersion}
          setVisible={hideNewDocument}
          siteId={params.siteId}
        />
      )}
      <DocDocumentsTable handleNewVersion={handleNewVersion} />
    </MainLayout>
  );
}
