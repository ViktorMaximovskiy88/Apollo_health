import { Form, Input, FormInstance } from 'antd';
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

export function DocDocumentInfoForm(props: {
  doc: DocDocument;
  form: FormInstance;
  onFieldChange: Function;
}) {
  const { doc } = props;
  return (
    <>
      <Name />
      <Hr />
      <DocumentClassification doc={doc} />
      <Hr />
      <DocumentFamily {...props} />
      <Hr />
      <DateFields {...props} />
      <Hr />
      <ExtractionFields doc={doc} />
      <Hr />
      <UrlFields doc={doc} />
    </>
  );
}
