import { Button } from 'antd';
import { useParams } from 'react-router-dom';
import { useRunExtractionTaskMutation } from './extractionsApi';
import { ExtractionTasksTable } from './ExtractionTasksTable';
import { MainLayout } from '../../components';
import { SiteMenu } from '../sites/SiteMenu';
import { useGetDocDocumentQuery } from '../doc_documents/docDocumentApi';

export function DocExtractionPage() {
  const params = useParams();
  const docId = params.docId;
  const [runExtractionForDoc] = useRunExtractionTaskMutation();
  const { data: doc } = useGetDocDocumentQuery(docId, { skip: !docId });

  if (!docId || !doc) return null;

  return (
    <MainLayout
      sidebar={<SiteMenu />}
      pageTitle={`Extractions - ${doc.name}`}
      pageToolbar={
        <Button className="ml-auto" onClick={() => runExtractionForDoc(docId)}>
          Run Extraction
        </Button>
      }
    >
      <ExtractionTasksTable />
    </MainLayout>
  );
}
