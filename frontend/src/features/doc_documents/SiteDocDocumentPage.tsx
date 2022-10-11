import { useState } from 'react';
import { Button } from 'antd';
import { useParams } from 'react-router-dom';

import { MainLayout } from '../../components';
import { SiteMenu } from '../sites/SiteMenu';

import { SiteDocDocumentsTable } from './SiteDocDocumentsTable';
import { AddDocumentModal } from '../collections/AddDocumentModal';
import { SiteDocDocument } from './types';

export function SiteDocDocumentsPage() {
  const [newDocumentModalOpen, setNewDocumentModalOpen] = useState(false);
  const [oldVersion, setOldVersion] = useState<any>();
  const [addNewDocument, setAddNewDocument] = useState<boolean>(false);
  const { siteId } = useParams();

  function handleNewVersion(data: SiteDocDocument, addNewDocument: boolean) {
    setOldVersion(data);
    setAddNewDocument(addNewDocument);
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
          <Button onClick={() => setNewDocumentModalOpen(true)} className="ml-auto">
            Create Document
          </Button>
        </>
      }
    >
      {newDocumentModalOpen && (
        <AddDocumentModal
          oldVersion={oldVersion}
          setOpen={hideNewDocument}
          siteId={siteId}
          addNewDocument={addNewDocument}
        />
      )}
      <SiteDocDocumentsTable handleNewVersion={handleNewVersion} />
    </MainLayout>
  );
}
