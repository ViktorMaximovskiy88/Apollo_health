import { Button } from 'antd';
import { MainLayout } from '../../components';
import { DocumentsTable } from './DocumentsTable';
import { SiteMenu } from './SiteMenu';

export function DocumentsPage() {
  return (
    <MainLayout
      sidebar={<SiteMenu />}
      pageTitle={'Documents'}
      pageToolbar={
        <>
          <Button className="ml-auto">Create Document</Button>
        </>
      }
    >
      <DocumentsTable />
    </MainLayout>
  );
}
