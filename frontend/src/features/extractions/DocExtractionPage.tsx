import { Button } from 'antd';
import { useParams } from 'react-router-dom';
import { useRunExtractionTaskMutation } from './extractionsApi';
import { useGetDocumentQuery } from '../retrieved_documents/documentsApi';
import { ExtractionTasksTable } from './ExtractionTasksTable';
import { PageLayout } from '../../components';

export function DocExtractionPage() {
  const params = useParams();
  const docId = params.docId;
  const [runExtractionForDoc] = useRunExtractionTaskMutation();
  const { data: doc } = useGetDocumentQuery(docId, { skip: !docId });

  if (!docId || !doc) return null;

  return (
    <PageLayout
      title={`Extractions - ${doc.name}`}
      toolbar={
        <>
          <Button className="ml-auto" onClick={() => runExtractionForDoc(docId)}>
            Run Extraction
          </Button>
        </>
      }
    >
      <ExtractionTasksTable />
    </PageLayout>
  );
}
