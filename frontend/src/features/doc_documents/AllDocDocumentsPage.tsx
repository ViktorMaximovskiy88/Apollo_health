import { DocDocumentsDataTable } from './AllDocDocumentsTable';
import { MainLayout } from '../../components';

export function AllDocDocumentsPage() {
  return (
    <MainLayout pageTitle={'Documents'}>
      <DocDocumentsDataTable />
    </MainLayout>
  );
}
