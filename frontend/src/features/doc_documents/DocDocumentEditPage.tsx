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
import { DocDocument, TherapyTag, IndicationTag } from './types';
import { useNavigate, useParams } from 'react-router-dom';
import { useCallback, useEffect, useState } from 'react';
import { maxBy, compact, groupBy, isEqual } from 'lodash';
import { WarningFilled } from '@ant-design/icons';

export function DocDocumentEditPage() {
  const navigate = useNavigate();
  const { docDocumentId: docId } = useParams();
  const { data: doc } = useGetDocDocumentQuery(docId);
  const [form] = useForm();
  const [updateDocDocument] = useUpdateDocDocumentMutation();
  const [tags, setTags] = useState([] as Array<TherapyTag | IndicationTag>);
  const [hasChanges, setHasChanges] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [pageNumber, setPageNumber] = useState(0);

  const finalEffectiveDate = useCallback(() => {
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
  }, [form]);

  useEffect(() => {
    if (doc) {
      const therapyTags = doc.therapy_tags.map((tag, i) => ({
        ...tag,
        id: `${i}-therapy`,
        _type: 'therapy',
        _normalized: `${tag.name.toLowerCase()}|${tag.text.toLowerCase()}`,
      }));
      const indicationTags = doc.indication_tags.map((tag, i) => ({
        ...tag,
        id: `${i}-indication`,
        _type: 'indication',
        _normalized: tag.text.toLowerCase(),
      }));
      setTags([...therapyTags, ...indicationTags]);
      finalEffectiveDate();
    }
  }, [doc, finalEffectiveDate]);

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

  function handleTagEdit(newTag: TherapyTag | IndicationTag) {
    setTags((prevState) => {
      const update = [...prevState];
      const index = update.findIndex((tag) => {
        return tag.id === newTag.id;
      });
      if (index > -1) {
        if (!isEqual(newTag, update[index])) setHasChanges(true);
        update[index] = newTag;
      }
      return update;
    });
  }

  async function onFinish(doc: Partial<DocDocument>) {
    setIsSaving(true);
    try {
      const tagsByType = groupBy(tags, '_type');
      await updateDocDocument({
        ...doc,
        indication_tags: (tagsByType['indication'] ?? []) as IndicationTag[],
        therapy_tags: (tagsByType['therapy'] ?? []) as TherapyTag[],
        _id: docId,
      });
      navigate(-1);
    } catch (error) {
      //  TODO real errors please
      console.error(error);
      setIsSaving(false);
    }
  }

  return (
    <MainLayout
      sectionToolbar={
        <div className="flex items-center space-x-4">
          {hasChanges && !isSaving && (
            <div className="text-orange-400">
              <WarningFilled /> You have unsaved changes
            </div>
          )}

          <Button
            disabled={isSaving}
            onClick={() => {
              navigate(-1);
            }}
          >
            Cancel
          </Button>
          <Button
            loading={isSaving}
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
            disabled={isSaving}
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
                  onAddTag={(tag: TherapyTag | IndicationTag) => {
                    tags.unshift(tag);
                    setTags([...tags]);
                    setHasChanges(true);
                  }}
                  onDeleteTag={(tag: any) => {
                    const index = tags.findIndex((t) => t.id === tag.id);
                    tags.splice(index, 1);
                    setTags([...tags]);
                    setHasChanges(true);
                  }}
                  onEditTag={handleTagEdit}
                  currentPage={pageNumber}
                />
              </Tabs.TabPane>
            </Tabs>
          </Form>
        </div>
        <div className="flex-1 h-full overflow-hidden ant-tabs-h-full">
          <RetrievedDocumentViewer
            doc={doc}
            docId={doc.retrieved_document_id}
            onPageChange={(page: number) => {
              setPageNumber(page);
            }}
          />
        </div>
      </div>
    </MainLayout>
  );
}
