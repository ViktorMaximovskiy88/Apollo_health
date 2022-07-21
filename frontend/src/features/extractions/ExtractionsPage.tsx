import { MainLayout } from '../../components';
import { ExtractedDocumentsTable } from './ExtractedDocumentsTable';
import { SiteMenu } from '../sites/SiteMenu';

export function ExtractionsPage() {
  return (
    <MainLayout pageTitle={'Extracted Documents'} sidebar={<SiteMenu />}>
      <ExtractedDocumentsTable />
    </MainLayout>
  );
}
