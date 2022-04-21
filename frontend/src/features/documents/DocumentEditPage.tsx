import { useParams } from "react-router-dom"
import { useGetDocumentQuery } from "./documentsApi";
import { Viewer, Worker } from '@react-pdf-viewer/core';
import { defaultLayoutPlugin } from '@react-pdf-viewer/default-layout';

import '@react-pdf-viewer/core/lib/styles/index.css';
import '@react-pdf-viewer/default-layout/lib/styles/index.css';
import Title from "antd/lib/typography/Title";
import { Table, Tabs } from "antd";
import { DocumentForm } from "./DocumentForm";
import tw from "twin.macro";

export function DocumentEditPage() {
    const params = useParams();
    const docId = params.docId;
    const { data: doc } = useGetDocumentQuery(docId);
    const defaultLayoutPluginInstance = defaultLayoutPlugin();
    if (!doc) return null;
    
    const columns = [
        { title: 'Key', dataIndex: 'key', key: 'key' },
        { title: 'Value', dataIndex: 'value', key: 'value' },
    ]
    const dataSource = Object.entries(doc.metadata || {}).map(([key,value]) => ({ key, value }))
    
    return <div className="flex flex-col h-full overflow-auto">
        <Title level={4}>{doc.name}</Title>
        <div className="flex space-x-4 h-full">
            <div className="w-1/2 h-full overflow-auto">
                <DocumentForm />
            </div>
            <Worker workerUrl="/pdf.worker.min.js">
                <div className="w-1/2 h-full overflow-auto">
                    <Tabs tabBarStyle={tw`h-10`}>
                    <Tabs.TabPane tab="Document" key="document">
                        <div className="h-full overflow-auto">
                        <Viewer
                            fileUrl={`/api/v1/documents/${docId}.pdf`}
                            plugins={[defaultLayoutPluginInstance]}
                        />
                        </div>
                    </Tabs.TabPane>
                    <Tabs.TabPane tab="Metadata" key="metadata">
                        <Table dataSource={dataSource} columns={columns}/>
                    </Tabs.TabPane>
                    </Tabs>
                </div>
            </Worker>
        </div>
    </div>
}
