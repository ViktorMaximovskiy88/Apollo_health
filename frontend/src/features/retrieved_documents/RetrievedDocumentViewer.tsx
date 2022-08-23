import { Viewer, PageChangeEvent } from '@react-pdf-viewer/core';
import { defaultLayoutPlugin } from '@react-pdf-viewer/default-layout';
import { OfficeFileLoader, TextFileLoader, CsvFileLoader, HtmlFileLoader } from '../../components';

import '@react-pdf-viewer/core/lib/styles/index.css';
import '@react-pdf-viewer/default-layout/lib/styles/index.css';

import { Table, Tabs } from 'antd';
import { useAccessToken } from '../../common/hooks';
import { baseApiUrl } from '../../app/base-api';

const columns = [
  { title: 'Key', dataIndex: 'key', key: 'key' },
  { title: 'Value', dataIndex: 'value', key: 'value' },
];

interface PropTypes {
  doc: any;
  docId: any;
  showMetadata?: boolean;
  onPageChange?: Function;
}

export function RetrievedDocumentViewer({
  docId,
  doc,
  showMetadata,
  onPageChange = () => {},
}: PropTypes) {
  const token = useAccessToken();
  const defaultLayoutPluginInstance = defaultLayoutPlugin();

  if (!(token && doc)) return null;

  const dataSource = Object.entries(doc.metadata || {}).map(([key, value]) => ({
    key,
    value,
  }));

  const viewer = ['pdf', 'html'].includes(doc.file_extension) ? (
    <Viewer
      withCredentials={true}
      fileUrl={`${baseApiUrl}/documents/${docId}.pdf`}
      plugins={[defaultLayoutPluginInstance]}
      onPageChange={(e: PageChangeEvent) => {
        // BUG: we dont get a page 0 event from the viewer ???
        // JumpToDestination maybe invert this...
        console.log('currentPage', e.currentPage);
        onPageChange(e.currentPage);
      }}
      httpHeaders={{
        Authorization: `Bearer ${token}`,
      }}
    />
  ) : ['xlsx', 'docx'].includes(doc.file_extension) ? (
    <OfficeFileLoader docId={docId} />
  ) : doc.file_extension === 'csv' ? (
    <CsvFileLoader docId={docId} />
  ) : doc.file_extension === 'html' ? (
    <HtmlFileLoader docId={docId} />
  ) : (
    <TextFileLoader docId={docId} />
  );

  if (showMetadata) {
    return (
      <Tabs className="h-full">
        <Tabs.TabPane tab="Document" key="document" className="h-full overflow-auto">
          {viewer}
        </Tabs.TabPane>
        <Tabs.TabPane tab="Metadata" key="properties">
          <Table dataSource={dataSource} columns={columns} pagination={false} />
        </Tabs.TabPane>
      </Tabs>
    );
  } else {
    return viewer;
  }
}
