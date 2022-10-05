import { useState } from 'react';
import { Button } from 'antd';
import { useParams } from 'react-router-dom';

import { MainLayout } from '../../components';
import { SiteMenu } from '../sites/SiteMenu';

import { SiteDocDocumentsTable } from './SiteDocDocumentsTable';
import { AddDocumentModal } from '../collections/addDocumentModal';
import { SiteDocDocument } from './types';

export function SiteDocDocumentsPage() {
  const [newDocumentModalVisible, setNewDocumentModalVisible] = useState(false);
  const [oldVersion, setOldVersion] = useState<any>();
  const { siteId } = useParams();

  function handleNewVersion(data: SiteDocDocument) {
    setOldVersion(data);
    setNewDocumentModalVisible(true);
  }

  function hideNewDocument(type: boolean) {
    setNewDocumentModalVisible(false);
    setOldVersion(null);
  }

  return (
    <MainLayout
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
        <AddDocumentModal oldVersion={oldVersion} setVisible={hideNewDocument} siteId={siteId} />
      )}
      <SiteDocDocumentsTable handleNewVersion={handleNewVersion} />
    </MainLayout>
  );
}
