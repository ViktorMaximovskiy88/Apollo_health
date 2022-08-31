import { DocDocumentsDataTable } from './DocDocumentsAllTable';
import { MainLayout } from '../../components';

export function DocDocumentsHomePage() {
  return (
    <MainLayout pageTitle={'Documents'}>
      <DocDocumentsDataTable />
    </MainLayout>
  );
}
