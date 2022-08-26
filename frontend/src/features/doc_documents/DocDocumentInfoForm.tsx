import { Form, Input } from 'antd';
import { Hr } from '../../components';
import { DateFields } from './DocDocumentDateFields';
import { DocumentClassification } from './DocDocumentClassificationFields';
import { ExtractionFields } from './DocDocumentExtractionFields';
import { UrlFields } from './DocDocumentUrlFields';
import { DocumentFamily } from './DocumentFamily';
import { Translation } from './TranslationSelector';

const Name = () => (
  <Form.Item name="name" label="Name" required={true}>
    <Input />
  </Form.Item>
);

export function DocDocumentInfoForm({ onFieldChange }: { onFieldChange: () => void }) {
  return (
    <>
      <Name />
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
      <UrlFields />
    </>
  );
}
