import { DocDocumentsDataTable } from './DocDocumentsDataTable';
import { MainLayout } from '../../components';

export function DocDocumentsHomePage() {
  return (
    <MainLayout pageTitle={'Documents'}>
      <DocDocumentsDataTable />
    </MainLayout>
  );
}
