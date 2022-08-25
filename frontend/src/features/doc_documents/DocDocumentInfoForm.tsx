import { Form, Input } from 'antd';
import { useParams } from 'react-router-dom';
import { useGetDocDocumentQuery } from './docDocumentApi';

import { Hr } from '../../components';
import { DateFields } from './DocDocumentDateFields';
import { DocumentClassification } from './DocDocumentClassificationFields';
import { ExtractionFields } from './DocDocumentExtractionFields';
import { DocDocumentLocations } from './DocDocumentLocations';
import { DocumentFamily } from './document_family/DocumentFamily';
import { Translation } from './TranslationSelector';

export function DocDocumentInfoForm({ onFieldChange }: { onFieldChange: Function }) {
  const { docDocumentId: docId } = useParams();
  const { data: doc } = useGetDocDocumentQuery(docId);
  if (!doc) return null;

  return (
    <>
      <Form.Item name="name" label="Name" required={true}>
        <Input />
      </Form.Item>
      <Hr />
      <DocumentClassification />
      <Translation />
      <Hr />
      <DocumentFamily />
      <Hr />
      <DateFields onFieldChange={onFieldChange} />
      <Hr />
      <ExtractionFields />
      <Hr />
      <DocDocumentLocations locations={doc.locations} />
    </>
  );
}
