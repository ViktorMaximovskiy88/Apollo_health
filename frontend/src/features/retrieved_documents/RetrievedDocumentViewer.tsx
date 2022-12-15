import { OfficeFileLoader, TextFileLoader, CsvFileLoader, GoogleDocLoader } from '../../components';

import '@react-pdf-viewer/core/lib/styles/index.css';
import '@react-pdf-viewer/default-layout/lib/styles/index.css';

import { Table, Tabs } from 'antd';
import { PDFFileLoader } from '../../components/PDFFileViewer';

const columns = [
  { title: 'Key', dataIndex: 'key', key: 'key' },
  { title: 'Value', dataIndex: 'value', key: 'value' },
];

interface PropTypes {
  doc: any;
  docId?: string; // RetrievedDocument ID
  showMetadata?: boolean;
  onPageChange?: Function;
}

export function FileTypeViewer({ docId, doc, onPageChange = () => {} }: PropTypes) {
  if (!doc || !docId) return null;
  console.log(docId, doc, 'test');
  return ['pdf', 'html'].includes(doc.file_extension) ? (
    <PDFFileLoader docId={docId} onPageChange={onPageChange} />
  ) : ['xlsx', 'xls', 'doc'].includes(doc.file_extension) ? (
    <OfficeFileLoader docId={docId} />
  ) : doc.file_extension === 'docx' ? (
    <GoogleDocLoader docId={docId} />
  ) : doc.file_extension === 'csv' ? (
    <CsvFileLoader docId={docId} />
  ) : (
    <TextFileLoader docId={docId} />
  );
}

export function RetrievedDocumentViewer({
  docId,
  doc,
  showMetadata,
  onPageChange = () => {},
}: PropTypes) {
  if (!doc) return null;
  const dataSource = Object.entries(doc.metadata || {}).map(([key, value]) => ({
    key,
    value,
  }));

  if (showMetadata) {
    return (
      <Tabs
        className="h-full"
        items={[
          {
            key: 'document',
            label: 'Document',
            className: 'h-full overflow-auto',
            children: <FileTypeViewer doc={doc} onPageChange={onPageChange} docId={docId} />,
          },
          {
            key: 'properties',
            label: 'Metadata',
            className: 'h-full overflow-auto',
            children: <Table dataSource={dataSource} columns={columns} pagination={false} />,
          },
        ]}
      />
    );
  } else {
    return <FileTypeViewer doc={doc} onPageChange={onPageChange} docId={docId} />;
  }
}
