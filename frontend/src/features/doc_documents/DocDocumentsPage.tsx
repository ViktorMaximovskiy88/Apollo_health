import { DocDocumentsDataTable } from './DocDocumentsTable';
import { MainLayout } from '../../components';

export function DocDocumentsPage() {
  return (
    <MainLayout pageTitle={'Documents'}>
      <DocDocumentsDataTable />
    </MainLayout>
  );
}
