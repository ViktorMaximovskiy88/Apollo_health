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
import { useEffect, useState } from 'react';
import groupBy from 'lodash.groupby';
import compact from 'lodash.compact';
import maxBy from 'lodash.maxby';
import { WarningFilled } from '@ant-design/icons';

export function DocDocumentEditPage() {
  const navigate = useNavigate();
  const { docDocumentId: docId } = useParams();
  const { data: doc } = useGetDocDocumentQuery(docId);
  const [form] = useForm();
  const [updateDocDocument] = useUpdateDocDocumentMutation();
  const [tags, setTags] = useState([] as BaseDocTag[]);
  const [hasChanges, setHasChanges] = useState(false);

  useEffect(() => {
    if (doc) {
      const therapyTags = doc.therapy_tags.map((tag) => ({ ...tag, type: 'therapy' }));
      const indicationTags = doc.indication_tags.map((tag) => ({ ...tag, type: 'indication' }));
      setTags([...therapyTags, ...indicationTags]);
      finalEffectiveDate();
    }
  }, [doc]);

  if (!doc) {
    return <></>;
  }

  const initialValues = {
    ...doc,
    final_effective_date: dateToMoment(doc.final_effective_date),
    effective_date: dateToMoment(doc.effective_date),
    end_date: dateToMoment(doc.end_date),
    last_updated_date: dateToMoment(doc.last_updated_date),
    next_review_date: dateToMoment(doc.next_review_date),
    next_update_date: dateToMoment(doc.next_update_date),
    published_date: dateToMoment(doc.published_date),
    last_reviewed_date: dateToMoment(doc.last_reviewed_date),
    first_collected_date: dateToMoment(doc.first_collected_date),
    last_collected_date: dateToMoment(doc.last_collected_date),
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

  function finalEffectiveDate() {
    const values = form.getFieldsValue(true);
    const computeFromFields = compact([
      dateToMoment(values.effective_date),
      dateToMoment(values.last_reviewed_date),
      dateToMoment(values.last_updated_date),
    ]);

    const finalEffectiveDate =
      computeFromFields.length > 0
        ? maxBy(computeFromFields, (date) => date.unix())
        : values.first_collected_date;

    form.setFieldsValue({
      final_effective_date: finalEffectiveDate.startOf('day'),
    });
  }

  return (
    <MainLayout
      sectionToolbar={
        <div className="flex items-center space-x-4">
          {hasChanges && (
            <div className="text-orange-400">
              <WarningFilled /> You have unsaved changes
            </div>
          )}

          <Button
            onClick={() => {
              navigate(-1);
            }}
          >
            Cancel
          </Button>
          <Button
            type="primary"
            onClick={() => {
              form.submit();
            }}
          >
            Submit
          </Button>
        </div>
      }
    >
      <div className="flex space-x-4 overflow-hidden h-full">
        <div className="flex-1 h-full overflow-hidden">
          <Form
            onFieldsChange={() => {
              setHasChanges(true);
              finalEffectiveDate();
            }}
            className="h-full"
            layout="vertical"
            form={form}
            requiredMark={false}
            initialValues={initialValues}
            onFinish={onFinish}
          >
            <Tabs className="h-full ant-tabs-h-full">
              <Tabs.TabPane tab="Info" key="info" className="bg-white p-4 overflow-auto">
                <DocDocumentInfoForm
                  doc={doc}
                  form={form}
                  onFieldChange={() => {
                    setHasChanges(true);
                    finalEffectiveDate();
                  }}
                />
              </Tabs.TabPane>
              <Tabs.TabPane tab="Tags" key="tags" className="bg-white p-4 h-full">
                <DocDocumentTagForm
                  tags={tags}
                  onAddTag={(tag: BaseDocTag) => {
                    tags.unshift(tag);
                    setTags([...tags]);
                    setHasChanges(true);
                  }}
                  onDeleteTag={(tag: any) => {
                    const index = tags.findIndex((t) => t.code === tag.code);
                    tags.splice(index, 1);
                    setTags([...tags]);
                    setHasChanges(true);
                  }}
                  onEditTag={(tag: any) => {
                    console.log('editing tag', tag);
                    setHasChanges(true);
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
