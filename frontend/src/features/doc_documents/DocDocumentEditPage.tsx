import { Button } from 'antd';
import { useGetDocDocumentQuery, useUpdateDocDocumentMutation } from './docDocumentApi';
import { DocDocumentEditForm } from './DocDocumentEditForm';
import { RetrievedDocumentViewer } from '../retrieved_documents/RetrievedDocumentViewer';
import { MainLayout } from '../../components';
import { useForm } from 'antd/lib/form/Form';
import { useNavigate, useParams } from 'react-router-dom';
import { useState } from 'react';
import { WarningFilled } from '@ant-design/icons';
import { DocDocument } from './types';

export function DocDocumentEditPage() {
  const navigate = useNavigate();
  const { docDocumentId: docId } = useParams();
  const { data: doc } = useGetDocDocumentQuery(docId, { refetchOnMountOrArgChange: true });

  const [form] = useForm();
  const [isSaving, setIsSaving] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);
  const [pageNumber, setPageNumber] = useState(0);
  const [updateDocDocumentMutation] = useUpdateDocDocumentMutation();
  const updateDocDocument = async (doc: Partial<DocDocument>): Promise<void> => {
    await updateDocDocumentMutation(doc);
    navigate(-1);
  };

  if (!doc || !docId) return null;

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
            disabled={isSaving}
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
          setIsSaving={setIsSaving}
          setHasChanges={setHasChanges}
          form={form}
          pageNumber={pageNumber}
          onSubmit={updateDocDocument}
          docId={docId}
        />
        <div className="flex-1 h-full overflow-hidden ant-tabs-h-full">
          <RetrievedDocumentViewer
            doc={doc}
            docId={doc.retrieved_document_id}
            onPageChange={(page: number) => {
              setPageNumber(page);
            }}
            showMetadata
          />
        </div>
      </div>
    </MainLayout>
  );
}
