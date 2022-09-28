import { useState } from 'react';
import { MainLayout } from '../../../components';
import { DocumentFamilyTable } from './DocumentFamilyDataTable';
import { DocumentFamily } from './types';

export function DocumentFamilyHomePage() {
  const [oldVersion, setOldVersion] = useState<any>();

  function handleNewVersion(data: DocumentFamily) {
    setOldVersion(data);
  }

  return (
    <MainLayout pageTitle={'Document Family'}>
      <DocumentFamilyTable handleNewVersion={handleNewVersion} />
    </MainLayout>
  );
}
