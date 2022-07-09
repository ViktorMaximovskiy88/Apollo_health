import { Button } from 'antd';
import Title from 'antd/lib/typography/Title';
import { useParams } from 'react-router-dom';
import {
  useRunExtractionTaskMutation,
} from './extractionsApi';
import { useGetDocumentQuery } from '../retrieved_documents/documentsApi';
import { ExtractionTasksTable } from './ExtractionTasksTable';

export function DocExtractionPage() {
  const params = useParams();
  const docId = params.docId;
  const [runExtractionForDoc] = useRunExtractionTaskMutation();
  const { data: doc } = useGetDocumentQuery(docId, { skip: !docId });

  if (!docId || !doc) return null;

  return <>
    <div className="flex">
      <Title className="inline-block" level={4}>
        Extractions - {doc.name}
      </Title>
      <Button className="ml-auto" onClick={() => runExtractionForDoc(docId)}>
        Run Extraction
      </Button>
    </div>
    <ExtractionTasksTable />
  </>;
}
