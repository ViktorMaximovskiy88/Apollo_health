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
        <div className="flex-1 h-full overflow-hidden">
          <Tabs className="h-full ant-tabs-h-full ">
            <Tabs.TabPane tab="Info" key="info" className="bg-white p-4 overflow-auto">
              <DocDocumentInfoForm doc={doc} />
            </Tabs.TabPane>
            <Tabs.TabPane tab="Tags" key="tags" className="bg-white p-4 h-full">
              <DocDocumentTagForm doc={doc} />
            </Tabs.TabPane>
          </Tabs>
        </div>
        <div className="flex-1 h-full overflow-hidden ant-tabs-h-full">
          <RetrievedDocumentViewer doc={doc} docId={doc.retrieved_document_id} />
        </div>
      </div>
    </MainLayout>
  );
}
