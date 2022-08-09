import { Form, Input } from 'antd';
import { Hr } from '../../components';
import { DocDocument } from './types';
import { DateFields } from './DocDocumentDateFields';
import { DocumentClassification } from './DocDocumentClassificationFields';
import { ExtractionFields } from './DocDocumentExtractionFields';
import { UrlFields } from './DocDocumentUrlFields';
import { DocumentFamily } from './DocumentFamilyField';

const Name = () => (
  <Form.Item name="name" label="Name" required={true}>
    <Input />
  </Form.Item>
);

export function DocDocumentInfoForm({
  doc,
  onFieldChange,
}: {
  doc: DocDocument;
  onFieldChange: Function;
}) {
  return (
    <>
      <Name />
      <Hr />
      <DocumentClassification />
      <Hr />
      <DocumentFamily />
      <Hr />
      <DateFields doc={doc} onFieldChange={onFieldChange} />
      <Hr />
      <ExtractionFields doc={doc} />
      <Hr />
      <UrlFields doc={doc} />
    </>
  );
}
