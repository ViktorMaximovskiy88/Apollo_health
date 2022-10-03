import { MainLayout } from '../../../components';
import { DocumentFamilyTable } from './DocumentFamilyDataTable';

export function DocumentFamilyHomePage() {
  return (
    <MainLayout pageTitle={'Document Family'}>
      <DocumentFamilyTable />
    </MainLayout>
  );
}
