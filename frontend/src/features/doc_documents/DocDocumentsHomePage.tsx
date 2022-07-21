import { Layout } from 'antd';
import Title from 'antd/lib/typography/Title';
import { DocDocumentsDataTable } from './DocDocumentsDataTable';

export function DocDocumentsHomePage() {
  return (
    <Layout className="p-4 bg-transparent">
      <div className="flex">
        <Title className="inline-block" level={4}>
          Documents
        </Title>
      </div>
      <DocDocumentsDataTable />
    </Layout>
  );
}
