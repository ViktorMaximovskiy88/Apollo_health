import { ExtractionResultsDataTable } from '../extractions/ExtractionResultsDataTable';
import { DocDocument } from './types';

export function DocDocumentExtractionTab(props: { doc: DocDocument }) {
  return <ExtractionResultsDataTable extractionId={props.doc.content_extraction_task_id} />;
}
