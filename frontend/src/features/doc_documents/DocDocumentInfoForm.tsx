import { Form, Input } from 'antd';
import { Hr } from '../../components';
import { DateFields } from './DocDocumentDateFields';
import { DocumentClassification } from './DocDocumentClassificationFields';
import { ExtractionFields } from './DocDocumentExtractionFields';
import { UrlFields } from './DocDocumentUrlFields';
import { DocumentFamily } from './DocumentFamily';

const Name = () => (
  <Form.Item name="name" label="Name" required={true}>
    <Input />
  </Form.Item>
);

export function DocDocumentInfoForm({ onFieldChange }: { onFieldChange: Function }) {
  return (
    <>
      <Name />
      <Hr />
      <DocumentClassification />
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
