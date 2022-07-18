import { PageHeader, PageLayout } from '../../components';
import { ExtractedDocumentsTable } from './ExtractedDocumentsTable';

export function ExtractionsPage() {
  return (
    <PageLayout>
      <PageHeader header={'Extracted Documents'} />
      <ExtractedDocumentsTable />
    </PageLayout>
  );
}
