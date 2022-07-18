import Layout from 'antd/lib/layout/layout';
import Title from 'antd/lib/typography/Title';
import { useParams } from 'react-router-dom';
import { useGetDocDocumentQuery } from './docDocumentApi';
import { DocDocumentForm } from './DocDocumentForm';
import { RetrievedDocumentViewer } from '../retrieved_documents/RetrievedDocumentViewer';

export function DocDocumentEditPage() {
  const { docDocumentId: docId } = useParams();
  const { data: doc } = useGetDocDocumentQuery(docId);

  if (!doc) {
    return <></>;
  }

  return (
    <Layout className="p-4 bg-transparent">
      <Title level={1}>{doc.name}</Title>
      <div className="flex space-x-4 overflow-hidden h-full">
        <div className="flex-1 h-full overflow-auto">
          <DocDocumentForm doc={doc} />
        </div>
        <div className="flex-1 h-full overflow-hidden ant-tabs-pdf-viewer">
          <RetrievedDocumentViewer doc={doc} docId={doc.retrieved_document_id} />
        </div>
      </div>
    </Layout>
  );
}
