import { Button } from 'antd';
import { useGetDocDocumentQuery } from './docDocumentApi';
import { DocDocumentEditForm } from './DocDocumentEditForm';
import { RetrievedDocumentViewer } from '../retrieved_documents/RetrievedDocumentViewer';
import { MainLayout } from '../../components';
import { useForm } from 'antd/lib/form/Form';
import { useUpdateDocDocumentMutation } from './docDocumentApi';
import { DocDocument, TherapyTag, IndicationTag } from './types';
import { useNavigate, useParams } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { groupBy } from 'lodash';
import { WarningFilled } from '@ant-design/icons';

const useTagsState = (
  doc?: DocDocument
): [Array<TherapyTag | IndicationTag>, (tags: Array<TherapyTag | IndicationTag>) => void] => {
  const [tags, setTags] = useState([] as Array<TherapyTag | IndicationTag>);

  useEffect(() => {
    if (!doc) return;

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
  }, [doc]);

  return [tags, setTags];
};

const useOnFinish = (
  tags: Array<TherapyTag | IndicationTag>
): [(doc: Partial<DocDocument>) => Promise<void>, boolean] => {
  const navigate = useNavigate();
  const { docDocumentId: docId } = useParams();
  const [isSaving, setIsSaving] = useState(false);
  const [updateDocDocument] = useUpdateDocDocumentMutation();

  const onFinish = async (doc: Partial<DocDocument>): Promise<void> => {
    if (!doc) return;

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
  };

  return [onFinish, isSaving];
};

export function DocDocumentEditPage() {
  const navigate = useNavigate();
  const { docDocumentId: docId } = useParams();
  const { data: doc } = useGetDocDocumentQuery(docId);
  const [form] = useForm();
  const [tags, setTags] = useTagsState(doc);
  const [hasChanges, setHasChanges] = useState(false);
  const [pageNumber, setPageNumber] = useState(0);
  const [onFinish, isSaving] = useOnFinish(tags);

  if (!doc) {
    return <></>;
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
        <DocDocumentEditForm
          isSaving={isSaving}
          setHasChanges={setHasChanges}
          form={form}
          doc={doc}
          tags={tags}
          setTags={setTags}
          pageNumber={pageNumber}
          onFinish={onFinish}
        />
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
