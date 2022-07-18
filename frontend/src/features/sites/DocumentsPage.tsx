import { Button } from 'antd';
import { PageLayout } from '../../components';
import { DocumentsTable } from './DocumentsTable';

export function DocumentsPage() {
  return (
    <PageLayout
      title={'Documents'}
      toolbar={
        <>
          <Button className="ml-auto">Create Document</Button>
        </>
      }
    >
      <DocumentsTable />
    </PageLayout>
  );
}
