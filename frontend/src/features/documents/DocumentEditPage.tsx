import { useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useGetDocumentQuery } from './documentsApi';
import { Viewer, Worker } from '@react-pdf-viewer/core';

import '@react-pdf-viewer/core/lib/styles/index.css';
import '@react-pdf-viewer/default-layout/lib/styles/index.css';

import Title from 'antd/lib/typography/Title';
import { Table, Tabs } from 'antd';
import { DocumentForm } from './DocumentForm';
import tw from 'twin.macro';
import {client} from '../../app/base-api'
import useAccessToken from '../../app/use-access-token';


export function DocumentEditPage() {
  const params = useParams();
  const docId = params.docId;

  const { data: doc } = useGetDocumentQuery(docId);
  const token = useAccessToken()

  
  if (!token) return null;
  if (!doc) return null;

  const columns = [
    { title: 'Key', dataIndex: 'key', key: 'key' },
    { title: 'Value', dataIndex: 'value', key: 'value' },
  ];

  const dataSource = Object.entries(doc.metadata || {}).map(([key, value]) => ({
    key,
    value,
  }));

  return (
    <div className="flex flex-col h-full overflow-auto">
      <Title level={4}>{doc.name}</Title>
      <div className="flex space-x-4 overflow-auto flex-grow">
        <div className="w-1/2 h-full overflow-auto">
          <DocumentForm doc={doc} />
        </div>
        <Worker workerUrl="/pdf.worker.min.js">
          <div className="w-1/2 h-full overflow-auto ant-tabs-pdf-viewer">
            <Tabs className="h-full" tabBarStyle={tw`h-10`}>
              <Tabs.TabPane
                tab="Document"
                key="document"
                className="h-full overflow-auto"
              >
                <Viewer
                  withCredentials={true}
                  fileUrl={`/api/v1/documents/${docId}.pdf`}
                  httpHeaders={{
                    Authorization: `Bearer ${token}`,
                  }}
                />
              </Tabs.TabPane>
              <Tabs.TabPane tab="PDF Metadata" key="metadata">
                <Table
                  dataSource={dataSource}
                  columns={columns}
                  pagination={false}
                />
              </Tabs.TabPane>
            </Tabs>
          </div>
        </Worker>
      </div>
    </div>
  );
}
