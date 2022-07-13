import { useParams } from 'react-router-dom';
import { useGetDocumentQuery } from './documentsApi';

import '@react-pdf-viewer/core/lib/styles/index.css';
import '@react-pdf-viewer/default-layout/lib/styles/index.css';

import Title from 'antd/lib/typography/Title';
import { DocumentForm } from './DocumentForm';
import { RetrievedDocumentViewer } from './RetrievedDocumentViewer';

export function DocumentEditPage() {
  const params = useParams();
  const docId = params.docId;

  const { data: doc } = useGetDocumentQuery(docId);

  if (!doc) {
    return <></>;
  }

  return (
    <div className="flex flex-col h-full overflow-hidden">
      <Title level={4}>{doc.name}</Title>
      <div className="flex space-x-4 overflow-auto flex-grow">
        <div className="w-1/2 h-full overflow-auto">
          <DocumentForm doc={doc} />
        </div>
        <div className="w-1/2 h-full overflow-auto ant-tabs-pdf-viewer">
          <RetrievedDocumentViewer doc={doc} docId={docId} />
        </div>
      </div>
    </div>
  );
}
