import { Form, FormInstance, Tabs } from 'antd';
import { DocDocument, IndicationTag, TherapyTag } from './types';
import { DocDocumentTagForm } from './DocDocumentTagForm';
import { dateToMoment } from '../../common';
import { useCallback, useEffect, useState } from 'react';
import { compact, groupBy, isEqual, maxBy } from 'lodash';
import { DocDocumentInfoForm } from './DocDocumentInfoForm';
import { DocDocumentLocationForm } from './locations/DocDocumentLocationForm';
import { useNavigate } from 'react-router-dom';
import { useGetDocDocumentQuery } from './docDocumentApi';

const useCalculateFinalEffectiveDate = (form: FormInstance): (() => void) => {
  const calculateFinalEffectiveDate = useCallback(() => {
    const values = form.getFieldsValue(true);
    const computeFromFields = compact([
      dateToMoment(values.effective_date),
      dateToMoment(values.last_reviewed_date),
      dateToMoment(values.last_updated_date),
    ]);

    const finalEffectiveDate: moment.Moment =
      computeFromFields.length > 0
        ? maxBy(computeFromFields, (date) => date.unix())
        : values.first_collected_date;

    form.setFieldsValue({
      final_effective_date: finalEffectiveDate.startOf('day'),
    });
  }, [form]);

  return calculateFinalEffectiveDate;
};

const useTagsState = (
  docId: string
): [Array<TherapyTag | IndicationTag>, (tags: Array<TherapyTag | IndicationTag>) => void] => {
  const { data: doc } = useGetDocDocumentQuery(docId);

  const [tags, setTags] = useState<Array<TherapyTag | IndicationTag>>([]);

  useEffect(() => {
    if (!doc) return;

    const therapyTags: TherapyTag[] = doc.therapy_tags.map((tag, i) => ({
      ...tag,
      id: `${i}-therapy`,
      _type: 'therapy',
      _normalized: `${tag.name.toLowerCase()}|${tag.text.toLowerCase()}`,
    }));
    const indicationTags: IndicationTag[] = doc.indication_tags.map((tag, i) => ({
      ...tag,
      id: `${i}-indication`,
      _type: 'indication',
      _normalized: tag.text.toLowerCase(),
    }));
    setTags([...therapyTags, ...indicationTags]);
  }, [doc]);

  return [tags, setTags];
};

interface UseOnFinishType {
  onSubmit: (doc: Partial<DocDocument>) => Promise<void>;
  tags: Array<TherapyTag | IndicationTag>;
  setIsSaving: (isSaving: boolean) => void;
  docId: string;
}
const useOnFinish = ({
  onSubmit,
  tags,
  setIsSaving,
  docId,
}: UseOnFinishType): ((doc: Partial<DocDocument>) => void) => {
  const navigate = useNavigate();

  const onFinish = async (submittedDoc: Partial<DocDocument>): Promise<void> => {
    if (!submittedDoc) return;

    setIsSaving(true);

    try {
      const tagsByType = groupBy(tags, '_type');

      await onSubmit({
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
  onSubmit: (doc: Partial<DocDocument>) => Promise<void>;
  docId: string;
}

export function DocDocumentEditForm({
  isSaving,
  setIsSaving,
  setHasChanges,
  form,
  pageNumber,
  onSubmit,
  docId,
}: EditFormPropTypes) {
  const { data: doc } = useGetDocDocumentQuery(docId);

  const calculateFinalEffectiveDate = useCalculateFinalEffectiveDate(form);
  useEffect(() => {
    if (!doc) return;
    calculateFinalEffectiveDate();
  }, [doc, calculateFinalEffectiveDate]);

  const [tags, setTags] = useTagsState(docId);
  const onFinish = useOnFinish({ onSubmit, tags, setIsSaving, docId });

  function handleTagEdit(newTag: TherapyTag | IndicationTag) {
    const update = [...tags];
    const index = update.findIndex((tag) => {
      return tag.id === newTag.id;
    });
    if (index > -1) {
      if (!isEqual(newTag, update[index])) setHasChanges(true);
      update[index] = newTag;
    }
    setTags(update);
  }

  if (!doc) return null;
  const initialValues = buildInitialValues(doc);

  return (
    <div className="flex-1 h-full overflow-hidden">
      <Form
        disabled={isSaving}
        onFieldsChange={() => {
          setHasChanges(true);
          calculateFinalEffectiveDate();
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
              onFieldChange={() => {
                setHasChanges(true);
                calculateFinalEffectiveDate();
              }}
            />
          </Tabs.TabPane>
          <Tabs.TabPane tab="Tags" key="tags" className="bg-white p-4 h-full">
            <DocDocumentTagForm
              tags={tags}
              onAddTag={(tag: TherapyTag | IndicationTag) => {
                setTags([tag, ...tags]);
                setHasChanges(true);
              }}
              onDeleteTag={(tag: any) => {
                setTags(tags.filter((t) => t.id !== tag.id));
                setHasChanges(true);
              }}
              onEditTag={handleTagEdit}
              currentPage={pageNumber}
            />
          </Tabs.TabPane>
          <Tabs.TabPane tab="Sites" key="sites" className="bg-white p-4 overflow-auto">
            <DocDocumentLocationForm locations={doc.locations} docDocument={doc} />
          </Tabs.TabPane>
        </Tabs>
      </Form>
    </div>
  );
}
