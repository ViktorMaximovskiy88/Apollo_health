import { Button } from 'antd';
import Title from 'antd/lib/typography/Title';
import { DocumentsTable } from './DocumentsTable';

export function DocumentsPage() {
  return (
    <>
      <div className="flex">
        <Title className="inline-block" level={4}>
          Documents
        </Title>
        <Button className="ml-auto">Create Document</Button>
      </div>
      <DocumentsTable />
    </>
  );
}
