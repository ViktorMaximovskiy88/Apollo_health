import { DocDocumentsDataTable } from './DocDocumentsDataTable';
import { MainLayout, PageLayout } from '../../components';

export function DocDocumentsHomePage() {
  return (
    <MainLayout pageTitle={'Documents'}>
      <DocDocumentsDataTable />
    </MainLayout>
  );
}
