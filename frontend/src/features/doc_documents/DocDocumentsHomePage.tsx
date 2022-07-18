import { DocDocumentsDataTable } from './DocDocumentsDataTable';
import { PageLayout } from '../../components';

export function DocDocumentsHomePage() {
  return (
    <PageLayout title={'Documents'}>
      <DocDocumentsDataTable />
    </PageLayout>
  );
}
