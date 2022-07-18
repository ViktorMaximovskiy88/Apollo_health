import { PageLayout } from '../../components';
import { ExtractedDocumentsTable } from './ExtractedDocumentsTable';

export function ExtractionsPage() {
  return (
    <PageLayout title={'Extracted Documents'}>
      <ExtractedDocumentsTable />
    </PageLayout>
  );
}
