import { useState } from 'react';
import { Button, notification } from 'antd';
import { useParams } from 'react-router-dom';

import { MainLayout } from '../../components';
import { SiteMenu } from '../sites/SiteMenu';

import { useLazyProcessSiteLineageQuery } from '../sites/sitesApi';
import { SiteDocDocumentsTable } from './SiteDocDocumentsTable';
import { AddDocumentModal } from '../collections/addDocumentModal';
import { SiteDocDocument } from './types';

export function SiteDocDocumentsPage() {
  const [processSiteLineage] = useLazyProcessSiteLineageQuery();
  const [newDocumentModalVisible, setNewDocumentModalVisible] = useState(false);
  const [oldVersion, setOldVersion] = useState<any>();
  const { siteId } = useParams();

  const openNotification = () => {
    notification.success({
      message: 'Processing lineage...',
    });
  };

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
      pageTitle={'Documents'}
      sidebar={<SiteMenu />}
      pageToolbar={
        <>
          <Button
            onClick={() => {
              processSiteLineage(siteId);
              openNotification();
            }}
            className="ml-auto"
          >
            Reprocess Lineage
          </Button>

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
