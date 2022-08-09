import { Form, FormInstance, Tabs } from 'antd';
import { DocDocument, IndicationTag, TherapyTag } from './types';
import { DocDocumentTagForm } from './DocDocumentTagForm';
import { dateToMoment } from '../../common';
import { useCallback, useEffect } from 'react';
import { compact, maxBy } from 'lodash';
import { DocDocumentInfoForm } from './DocDocumentInfoForm';

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

const buildInitialValues = (doc: DocDocument) => ({
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
});

interface EditFormPropTypes {
  isSaving: boolean;
  setHasChanges: (hasChanges: boolean) => void;
  form: FormInstance;
  doc: DocDocument;
  tags: Array<TherapyTag | IndicationTag>;
  setTags: (tags: Array<TherapyTag | IndicationTag>) => void;
  pageNumber: number;
  onFinish: (doc: Partial<DocDocument>) => Promise<void>;
}
export function DocDocumentEditForm({
  isSaving,
  setHasChanges,
  form,
  doc,
  tags,
  setTags,
  pageNumber,
  onFinish,
}: EditFormPropTypes) {
  const calculateFinalEffectiveDate = useCalculateFinalEffectiveDate(form);

  useEffect(() => {
    if (!doc) return;
    calculateFinalEffectiveDate();
  }, [doc, calculateFinalEffectiveDate]);

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
              doc={doc}
              form={form}
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
                setTags(tags.filter((t) => t.code !== tag.code));
                setHasChanges(true);
              }}
              onEditTag={(tag: TherapyTag | IndicationTag) => {}} // TODO: finish onEditTag
              currentPage={pageNumber}
            />
          </Tabs.TabPane>
        </Tabs>
      </Form>
    </div>
  );
}
