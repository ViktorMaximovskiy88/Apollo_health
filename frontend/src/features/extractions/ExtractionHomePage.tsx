import { Button, Table } from 'antd';
import Title from 'antd/lib/typography/Title';

export function ExtractionHomePage() {
  const columns = [{}];
  const documents = [{}];
  return (
    <div>
      <div className="flex">
        <Title className="inline-block" level={4}>
          Content Extraction
        </Title>
      </div>
      <Table dataSource={documents} columns={columns} />
    </div>
  );
}
