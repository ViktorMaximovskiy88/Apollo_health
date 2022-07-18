import { Button } from 'antd';
import Title from 'antd/lib/typography/Title';
import { useParams } from 'react-router-dom';
import { useRunExtractionTaskMutation } from './extractionsApi';
import { useGetDocumentQuery } from '../retrieved_documents/documentsApi';
import { ExtractionTasksTable } from './ExtractionTasksTable';
import { PageHeader, PageLayout } from '../../components';

export function DocExtractionPage() {
  const params = useParams();
  const docId = params.docId;
  const [runExtractionForDoc] = useRunExtractionTaskMutation();
  const { data: doc } = useGetDocumentQuery(docId, { skip: !docId });

  if (!docId || !doc) return null;

  return (
    <PageLayout>
      <PageHeader header={`Extractions - ${doc.name}`}>
        <Button className="ml-auto" onClick={() => runExtractionForDoc(docId)}>
          Run Extraction
        </Button>
      </PageHeader>
      <ExtractionTasksTable />
    </PageLayout>
  );
}
