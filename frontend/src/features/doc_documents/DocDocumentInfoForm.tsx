import { Form, Input } from 'antd';
import { useParams } from 'react-router-dom';
import { useGetDocDocumentQuery } from './docDocumentApi';

import { Hr } from '../../components';
import { DateFields } from './DocDocumentDateFields';
import { DocumentClassification } from './DocDocumentClassificationFields';
import { ExtractionFields } from './DocDocumentExtractionFields';
import { Translation } from './TranslationSelector';

export function DocDocumentInfoForm({ onFieldChange }: { onFieldChange: () => void }) {
  // bandaid fix; painted into a corner
  const { docDocumentId, itemId } = useParams();
  const docId = docDocumentId ?? itemId;
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
      <DateFields onFieldChange={onFieldChange} />
      <Hr />
      <ExtractionFields />
    </>
  );
}
