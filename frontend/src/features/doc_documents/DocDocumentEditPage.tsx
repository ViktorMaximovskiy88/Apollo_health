import { Button, Form } from 'antd';
import { useGetDocDocumentQuery } from './docDocumentApi';
import { DocDocumentInfoForm } from './DocDocumentInfoForm';
import { DocDocumentTagForm } from './DocDocumentTagForm';
import { RetrievedDocumentViewer } from '../retrieved_documents/RetrievedDocumentViewer';
import { MainLayout } from '../../components';
import { Tabs } from 'antd';
import { useForm } from 'antd/lib/form/Form';
import { dateToMoment } from '../../common/date';
import { useUpdateDocDocumentMutation } from './docDocumentApi';
import { DocDocument, BaseDocTag } from './types';
import { useNavigate, useParams } from 'react-router-dom';
import { useState } from 'react';
import groupBy from 'lodash.groupby';

export function DocDocumentEditPage() {
  const navigate = useNavigate();
  const { docDocumentId: docId } = useParams();
  const { data: doc } = useGetDocDocumentQuery(docId);
  const [form] = useForm();
  const [updateDocDocument] = useUpdateDocDocumentMutation();
  const [tags, setTags] = useState([...(doc?.therapy_tags ?? []), ...(doc?.indication_tags ?? [])]);

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

  async function onFinish(doc: Partial<DocDocument>) {
    const tagsByType = groupBy(tags, 'type');
    doc.indication_tags = tagsByType['indication'];
    doc.therapy_tags = tagsByType['therapy'];

    await updateDocDocument({
      ...doc,
      _id: docId,
    });
    navigate(-1);
  }

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
            onFinish={onFinish}
          >
            <Tabs className="h-full ant-tabs-h-full">
              <Tabs.TabPane tab="Info" key="info" className="bg-white p-4 overflow-auto">
                <DocDocumentInfoForm doc={doc} form={form} />
              </Tabs.TabPane>
              <Tabs.TabPane tab="Tags" key="tags" className="bg-white p-4 h-full">
                <DocDocumentTagForm
                  tags={tags}
                  onAddTag={(tag: BaseDocTag) => {
                    tags.unshift(tag);
                    setTags([...tags]);
                  }}
                  onDeleteTag={(tag: any) => {
                    const index = tags.findIndex((t) => t.code === tag.code);
                    tags.splice(index, 1);
                    setTags([...tags]);
                  }}
                  onEditTag={(tag: any) => {
                    console.log('editing tag');
                  }}
                />
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
