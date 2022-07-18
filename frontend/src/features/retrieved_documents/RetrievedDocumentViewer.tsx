import { Viewer, Worker } from '@react-pdf-viewer/core';
import { defaultLayoutPlugin } from '@react-pdf-viewer/default-layout';
import { OfficeFileLoader } from '../../components/OfficeFileViewer';

import '@react-pdf-viewer/core/lib/styles/index.css';
import '@react-pdf-viewer/default-layout/lib/styles/index.css';

import { Table, Tabs } from 'antd';
import tw from 'twin.macro';
import { useAccessToken } from '../../common/hooks';
import { baseApiUrl } from '../../app/base-api';

const columns = [
  { title: 'Key', dataIndex: 'key', key: 'key' },
  { title: 'Value', dataIndex: 'value', key: 'value' },
];

interface PropTypes {
  doc: any;
  docId: any;
}

export function RetrievedDocumentViewer({ docId, doc }: PropTypes) {
  const token = useAccessToken();
  const defaultLayoutPluginInstance = defaultLayoutPlugin();

  if (!(token && doc)) return null;

  const dataSource = Object.entries(doc.metadata || {}).map(([key, value]) => ({
    key,
    value,
  }));

  return (
    <Worker workerUrl="/pdf.worker.min.js">
      <Tabs className="h-full" tabBarStyle={tw`h-10`}>
        <Tabs.TabPane tab="Document" key="document" className="h-full overflow-auto">
          {doc.file_extension === 'pdf' ? (
            <Viewer
              withCredentials={true}
              fileUrl={`${baseApiUrl}/documents/${docId}.${doc.file_extension}`}
              plugins={[defaultLayoutPluginInstance]}
              httpHeaders={{
                Authorization: `Bearer ${token}`,
              }}
            />
          ) : (
            <OfficeFileLoader docId={docId} />
          )}
        </Tabs.TabPane>
        <Tabs.TabPane tab="Metadata" key="metadata">
          <Table dataSource={dataSource} columns={columns} pagination={false} />
        </Tabs.TabPane>
      </Tabs>
    </Worker>
  );
}
