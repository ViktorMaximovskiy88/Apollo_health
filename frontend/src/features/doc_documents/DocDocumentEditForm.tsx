import { useMemo } from 'react';
import { Form, FormInstance } from 'antd';
import { DocDocument, DocumentTag, UIIndicationTag, UITherapyTag } from './types';
import { DocDocumentTagForm } from './DocDocumentTagForm';
import { dateToMoment } from '../../common';
import { useCallback, useEffect, useState } from 'react';
import { isEqual } from 'lodash';
import { DocDocumentInfoForm } from './DocDocumentInfoForm';
import { DocDocumentLocations } from './locations/DocDocumentLocations';
import { useGetChangeLogQuery, useGetDocDocumentQuery } from './docDocumentApi';
import { DocDocumentExtractionTab } from './DocDocumentExtractionTab';
import { calculateFinalEffectiveFromValues } from './helpers';
import { DocStatusModal } from './DocStatusModal';
import { HashRoutedTabs } from '../../components/HashRoutedTabs';
import { CommentWall } from '../comments/CommentWall';
import { ChangeLogModal } from '../change-log/ChangeLogModal';

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

const useTagsState = (docId: string): [Array<DocumentTag>, (tags: Array<DocumentTag>) => void] => {
  const { data: doc } = useGetDocDocumentQuery(docId);

  const [tags, setTags] = useState<Array<DocumentTag>>([]);

  useEffect(() => {
    if (!doc) return;

    const therapyTags: UITherapyTag[] = doc.therapy_tags.map((tag, i) => ({
      ...tag,
      id: `${i}-therapy`,
      _type: 'therapy',
      _normalized: `${tag.name.toLowerCase()}|${tag.text.toLowerCase()}`,
    }));
    const indicationTags: UIIndicationTag[] = doc.indication_tags.map((tag, i) => ({
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
  tags: Array<DocumentTag>;
  setIsSaving: (isSaving: boolean) => void;
  docId: string;
}
const useOnFinish = ({
  onSubmit,
  tags,
  setIsSaving,
  docId,
}: UseOnFinishType): ((doc: Partial<DocDocument>) => void) => {
  const onFinish = async (submittedDoc: Partial<DocDocument>): Promise<void> => {
    if (!submittedDoc) return;

    setIsSaving(true);

    try {
      const indication_tags = [];
      const therapy_tags = [];
      for (const tag of tags) {
        if (tag._type === 'indication') {
          const { name, text, page, code, focus, update_status, text_area } =
            tag as UIIndicationTag;
          indication_tags.push({ name, text, page, code, focus, update_status, text_area });
        } else {
          const { name, text, page, score, code, focus, update_status, text_area } =
            tag as UITherapyTag;
          therapy_tags.push({ name, text, page, score, code, focus, update_status, text_area });
        }
      }

      submittedDoc.previous_par_id = submittedDoc.previous_par_id || null;
      submittedDoc.document_family_id = submittedDoc.document_family_id || null;

      await onSubmit({
        ...submittedDoc,
        indication_tags,
        therapy_tags,
        _id: docId,
      });
    } catch (error) {
      //  TODO real errors please
      console.error(error);
    }
    setIsSaving(false);
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

  function handleTagEdit(newTag: DocumentTag, updateTags: boolean = false) {
    const update = [...tags];
    const index = update.findIndex((tag) => {
      return tag.id === newTag.id;
    });
    if (index > -1) {
      if (updateTags) {
        update.forEach((tag) => {
          if (tag.id !== newTag.id && tag.name === newTag.name) {
            tag.focus = newTag.focus;
          }
        });
      }
      if (!isEqual(newTag, update[index])) setHasChanges(true);
      update[index] = newTag;
    }
    setTags(update);
  }

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
