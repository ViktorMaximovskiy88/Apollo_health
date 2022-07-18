import { Button } from 'antd';
import { PageHeader, PageLayout } from '../../components';
import { DocumentsTable } from './DocumentsTable';

export function DocumentsPage() {
  return (
    <PageLayout>
      <PageHeader header={'Documents'}>
        <Button className="ml-auto">Create Document</Button>
      </PageHeader>
      <DocumentsTable />
    </PageLayout>
  );
}
