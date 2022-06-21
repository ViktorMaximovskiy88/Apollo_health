import Title from 'antd/lib/typography/Title';
import { ExtractedDocumentsTable } from './ExtractedDocumentsTable';

export function ExtractionsPage() {
  return (
    <>
      <div className="flex">
        <Title className="inline-block" level={4}>
          Extracted Documents
        </Title>
      </div>
      <ExtractedDocumentsTable />
    </>
  );
}
