import { FormInstance } from 'antd';
import { useGetDocDocumentQuery } from '../doc_documents/docDocumentApi';
import { RetrievedDocumentViewer } from '../retrieved_documents/RetrievedDocumentViewer';
import { DocDocument } from '../doc_documents/types';
import { useState } from 'react';
import { DocDocumentEditForm } from '../doc_documents/DocDocumentEditForm';

interface DocDocumentClassificationPagePropTypes {
  docId: string;
  form: FormInstance;
  onSubmit: (doc: Partial<DocDocument>) => Promise<void>;
}
export function DocDocumentClassificationPage({
  docId,
  form,
  onSubmit,
}: DocDocumentClassificationPagePropTypes) {
  const { data: doc } = useGetDocDocumentQuery(docId);

  const [isSaving, setIsSaving] = useState(false);
  const [, setHasChanges] = useState(false);
  const [pageNumber, setPageNumber] = useState(0);

  if (!doc) return null;

  return (
    <div className="flex space-x-4 overflow-hidden h-full">
      <DocDocumentEditForm
        isSaving={isSaving}
        setIsSaving={setIsSaving}
        setHasChanges={setHasChanges}
        form={form}
        pageNumber={pageNumber}
        onSubmit={onSubmit}
        docId={docId}
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
  );
}
