import { useMemo } from 'react';
import { Form, FormInstance } from 'antd';

import { DocDocument, DocumentTag } from './types';
import { DocDocumentTagForm } from './DocDocumentTagForm';
import { dateToMoment } from '../../common';
import { useCallback, useEffect } from 'react';
import { DocDocumentInfoForm } from './DocDocumentInfoForm';
import { DocDocumentLocations } from './locations/DocDocumentLocations';
import { useGetChangeLogQuery, useGetDocDocumentQuery } from './docDocumentApi';
import { DocDocumentExtractionTab } from './DocDocumentExtractionTab';
import { calculateFinalEffectiveFromValues } from './helpers';
import { DocStatusModal } from './DocStatusModal';
import { HashRoutedTabs } from '../../components/HashRoutedTabs';
import { CommentWall } from '../comments/CommentWall';
import { ChangeLogModal } from '../change-log/ChangeLogModal';
import { useTagsState } from './useTagsState';
import { useOnFinish } from './useOnFinish';
import { focusDocumentTypes } from './useOnFinish';

const useCalculateFinalEffectiveDate = (form: FormInstance): (() => void) => {
  const calculateFinalEffectiveDate = useCallback(() => {
    const values = form.getFieldsValue(true);
    const finalEffectiveDate = calculateFinalEffectiveFromValues(values);
    form.setFieldsValue({
      final_effective_date: finalEffectiveDate?.startOf('day'),
    });
  }, [form]);

  return calculateFinalEffectiveDate;
};

const useSetDocumentTypeFocusTags = (form: FormInstance, tags: DocumentTag[]): (() => void) => {
  const setDocumentTypeFocusTags = useCallback(() => {
    const documentType = form.getFieldValue('document_type');
    if (focusDocumentTypes.includes(documentType)) {
      tags.forEach((tag) => {
        tag.focus = true;
      });
    }
  }, [form, tags]);

  return setDocumentTypeFocusTags;
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

  const { tags, setTags, handleTagEdit } = useTagsState({ docId, setHasChanges });
  const setDocumentTypeFocusTags = useSetDocumentTypeFocusTags(form, tags);
  const onFinish = useOnFinish({ onSubmit, tags, setIsSaving, docId });

  const initialValues = useMemo(() => (doc ? buildInitialValues(doc) : {}), [doc]);
  useEffect(() => {
    setHasChanges(false);
    form.setFieldsValue(initialValues);
    form.resetFields();
  }, [initialValues, setHasChanges, form]);

  if (!doc) return null;

  const tabs = [
    {
      label: 'Info',
      key: 'info',
      children: (
        <DocDocumentInfoForm
          onFieldChange={() => {
            setHasChanges(true);
            calculateFinalEffectiveDate();
            setDocumentTypeFocusTags();
          }}
        />
      ),
    },
    {
      label: 'Sites',
      key: 'sites',
      children: <DocDocumentLocations locations={doc.locations} />,
    },
    {
      label: 'Tags',
      key: 'tags',
      children: (
        <DocDocumentTagForm
          tags={tags}
          onDeleteTag={(tag: any) => {
            setTags(tags.filter((t) => t.id !== tag.id));
            setHasChanges(true);
          }}
          onEditTag={handleTagEdit}
          currentPage={pageNumber}
        />
      ),
    },
  ];

  if (doc?.content_extraction_task_id) {
    tabs.push({
      label: 'Extraction',
      key: 'extraction',
      children: <DocDocumentExtractionTab doc={doc} />,
    });
  }

  tabs.push({
    label: 'Notes',
    key: 'comments',
    children: <CommentWall targetId={doc._id} />,
  });

  return (
    <div className="flex-1 h-full overflow-hidden">
      <Form
        disabled={isSaving}
        onFieldsChange={() => {
          setHasChanges(true);
          calculateFinalEffectiveDate();
          setDocumentTypeFocusTags();
        }}
        className="h-full"
        layout="vertical"
        form={form}
        requiredMark={false}
        initialValues={initialValues}
        onFinish={onFinish}
      >
        <HashRoutedTabs
          tabBarExtraContent={
            <>
              <ChangeLogModal target={doc} useChangeLogQuery={useGetChangeLogQuery} />
              <DocStatusModal doc={doc} />
            </>
          }
          items={tabs}
          className="h-full ant-tabs-h-full"
        />
      </Form>
    </div>
  );
}
