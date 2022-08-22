import { Form, FormInstance, Tabs } from 'antd';
import { DocDocument, IndicationTag, TherapyTag } from '../doc_documents/types';
import { DocDocumentTagForm } from '../doc_documents/DocDocumentTagForm';
import { dateToMoment } from '../../common';
import { useCallback, useEffect, useState } from 'react';
import { compact, groupBy, maxBy } from 'lodash';
import { DocDocumentInfoForm } from '../doc_documents/DocDocumentInfoForm';
import { useNavigate, useParams } from 'react-router-dom';
import {
  useGetDocDocumentQuery,
  useUpdateDocDocumentMutation,
} from '../doc_documents/docDocumentApi';

const useCalculateFinalEffectiveDate = (form: FormInstance): (() => void) => {
  const calculateFinalEffectiveDate = useCallback(() => {
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

  return calculateFinalEffectiveDate;
};

const useTagsState = (): [
  Array<TherapyTag | IndicationTag>,
  (tags: Array<TherapyTag | IndicationTag>) => void
] => {
  const { docDocumentId: docId } = useParams();
  const { data: doc } = useGetDocDocumentQuery(docId);

  const [tags, setTags] = useState<Array<TherapyTag | IndicationTag>>([]);

  useEffect(() => {
    if (!doc) return;

    const therapyTags = doc.therapy_tags.map((tag) => ({
      ...tag,
      _type: 'therapy',
      _normalized: `${tag.name.toLowerCase()}|${tag.text.toLowerCase()}`,
    }));
    const indicationTags = doc.indication_tags.map((tag) => ({
      ...tag,
      _type: 'indication',
      _normalized: tag.text.toLowerCase(),
    }));
    setTags([...therapyTags, ...indicationTags]);
  }, [doc]);

  return [tags, setTags];
};

const useOnFinish = (
  tags: Array<TherapyTag | IndicationTag>,
  setIsSaving: (isSaving: boolean) => void
): ((doc: Partial<DocDocument>) => Promise<void>) => {
  const navigate = useNavigate();
  const { docDocumentId: docId } = useParams();

  const [updateDocDocument] = useUpdateDocDocumentMutation();

  const onFinish = async (submittedDoc: Partial<DocDocument>): Promise<void> => {
    if (!submittedDoc) return;

    setIsSaving(true);

    try {
      const tagsByType = groupBy(tags, '_type');
      await updateDocDocument({
        ...submittedDoc,
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
  };

  return onFinish;
};

const buildInitialValues = (doc: DocDocument) => ({
  ...doc,
  docId: doc._id,
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
});

interface EditFormPropTypes {
  isSaving: boolean;
  setIsSaving: (isSaving: boolean) => void;
  setHasChanges: (hasChanges: boolean) => void;
  form: FormInstance;
  pageNumber: number;
  onSubmit: (doc: Partial<DocDocument>) => void;
  docId: string;
}
export function DocDocumentEditForm(props: EditFormPropTypes) {
  const { data: doc } = useGetDocDocumentQuery(props.docId);

  const calculateFinalEffectiveDate = useCalculateFinalEffectiveDate(props.form);
  useEffect(() => {
    if (!doc) return;
    calculateFinalEffectiveDate();
  }, [doc, calculateFinalEffectiveDate]);

  const [tags, setTags] = useTagsState();
  const onFinish = useOnFinish(tags, props.setIsSaving);

  if (!doc) return null;
  const initialValues = buildInitialValues(doc);

  return (
    <div className="flex-1 h-full overflow-hidden">
      <Form
        disabled={props.isSaving}
        onFieldsChange={() => {
          props.setHasChanges(true);
          calculateFinalEffectiveDate();
        }}
        className="h-full"
        layout="vertical"
        form={props.form}
        requiredMark={false}
        initialValues={initialValues}
        onFinish={(doc: DocDocument) => {
          onFinish(doc);
          props.onSubmit(doc);
        }}
      >
        <Tabs className="h-full ant-tabs-h-full">
          <Tabs.TabPane tab="Info" key="info" className="bg-white p-4 overflow-auto">
            <DocDocumentInfoForm
              onFieldChange={() => {
                props.setHasChanges(true);
                calculateFinalEffectiveDate();
              }}
            />
          </Tabs.TabPane>
          <Tabs.TabPane tab="Tags" key="tags" className="bg-white p-4 h-full">
            <DocDocumentTagForm
              tags={tags}
              onAddTag={(tag: TherapyTag | IndicationTag) => {
                setTags([tag, ...tags]);
                props.setHasChanges(true);
              }}
              onDeleteTag={(tag: any) => {
                setTags(tags.filter((t) => t.code !== tag.code));
                props.setHasChanges(true);
              }}
              onEditTag={(tag: TherapyTag | IndicationTag) => {}} // TODO: finish onEditTag
              currentPage={props.pageNumber}
            />
          </Tabs.TabPane>
        </Tabs>
      </Form>
    </div>
  );
}
