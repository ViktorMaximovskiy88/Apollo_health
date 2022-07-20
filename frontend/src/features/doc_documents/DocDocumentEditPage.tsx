import { Button, Form } from 'antd';
import { useParams } from 'react-router-dom';
import { useGetDocDocumentQuery } from './docDocumentApi';
import { DocDocumentInfoForm } from './DocDocumentInfoForm';
import { DocDocumentTagForm } from './DocDocumentTagForm';
import { RetrievedDocumentViewer } from '../retrieved_documents/RetrievedDocumentViewer';
import { MainLayout } from '../../components';
import { Tabs } from 'antd';
import { useForm } from 'antd/lib/form/Form';
import { dateToMoment } from '../../common/date';
import { useUpdateDocDocumentMutation } from './docDocumentApi';

export function DocDocumentEditPage() {
  const { docDocumentId: docId } = useParams();
  const { data: doc } = useGetDocDocumentQuery(docId);
  const [form] = useForm();

  if (!doc) {
    return <></>;
  }

  const initialValues = {
    ...doc,
    effective_date: dateToMoment(doc.effective_date),
    end_date: dateToMoment(doc.end_date),
    last_updated_date: dateToMoment(doc.last_updated_date),
    next_review_date: dateToMoment(doc.next_review_date),
    next_update_date: dateToMoment(doc.next_update_date),
    published_date: dateToMoment(doc.published_date),
    last_reviewed_date: dateToMoment(doc.last_reviewed_date),
  };

  return (
    <MainLayout
      sectionToolbar={
        <>
          <Button>Cancel</Button>
          <Button
            type="primary"
            onClick={() => {
              form.submit();
            }}
          >
            Submit
          </Button>
        </>
      }
    >
      <div className="flex space-x-4 overflow-hidden h-full">
        <div className="flex-1 h-full overflow-hidden">
          <Form
            className="h-full"
            layout="vertical"
            form={form}
            requiredMark={false}
            initialValues={initialValues}
            onFinish={(values: any) => {
              console.log('values', values);
            }}
          >
            <Tabs className="h-full ant-tabs-h-full ">
              <Tabs.TabPane tab="Info" key="info" className="bg-white p-4 overflow-auto">
                <DocDocumentInfoForm doc={doc} form={form} />
              </Tabs.TabPane>
              <Tabs.TabPane tab="Tags" key="tags" className="bg-white p-4 h-full">
                <DocDocumentTagForm doc={doc} form={form} />
              </Tabs.TabPane>
            </Tabs>
          </Form>
        </div>
        <div className="flex-1 h-full overflow-hidden ant-tabs-h-full">
          <RetrievedDocumentViewer doc={doc} docId={doc.retrieved_document_id} />
        </div>
      </div>
    </MainLayout>
  );
}
