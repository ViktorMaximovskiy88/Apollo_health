import { Button } from 'antd';
import { useParams } from 'react-router-dom';
import { useGetDocDocumentQuery } from './docDocumentApi';
import { DocDocumentInfoForm } from './DocDocumentInfoForm';
import { DocDocumentTagForm } from './DocDocumentTagForm';
import { RetrievedDocumentViewer } from '../retrieved_documents/RetrievedDocumentViewer';
import { MainLayout } from '../../components';
import { Tabs } from 'antd';

export function DocDocumentEditPage() {
  const { docDocumentId: docId } = useParams();
  const { data: doc } = useGetDocDocumentQuery(docId);

  if (!doc) {
    return <></>;
  }

  return (
    <MainLayout
      sectionToolbar={
        <>
          <Button>Cancel</Button>
          <Button type="primary" htmlType="submit">
            Save
          </Button>
        </>
      }
    >
      <div className="flex space-x-4 overflow-hidden h-full">
        <div className="flex-1 h-full overflow-auto">
          <Tabs className="h-full">
            <Tabs.TabPane tab="Info" key="info" className="h-full overflow-auto bg-white p-4">
              <DocDocumentInfoForm doc={doc} />
            </Tabs.TabPane>
            <Tabs.TabPane tab="Tags" key="tags" className="h-full overflow-auto bg-white p-4">
              <DocDocumentTagForm doc={doc} />
            </Tabs.TabPane>
          </Tabs>
        </div>
        <div className="flex-1 h-full overflow-hidden ant-tabs-pdf-viewer">
          <RetrievedDocumentViewer doc={doc} docId={doc.retrieved_document_id} />
        </div>
      </div>
    </MainLayout>
  );
}
