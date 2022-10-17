import { Form, Input } from 'antd';

import { Hr } from '../../components';
import { DateFields } from './DocDocumentDateFields';
import { DocumentClassification } from './DocDocumentClassificationFields';
import { ExtractionFields } from './DocDocumentExtractionFields';
import { Translation } from './TranslationSelector';
import { DocDocumentInfoFormFamilyField } from './DocDocumentInfoFormFamilyField';

interface DocDocumentInfoTypes {
  onFieldChange: () => void;
}
export function DocDocumentInfoForm({ onFieldChange }: DocDocumentInfoTypes) {
  return (
    <div className="p-2 bg-white">
      <Form.Item name="name" label="Name" required={true}>
        <Input />
      </Form.Item>
      <Hr />
      <DocumentClassification />
      <Hr />
      <DateFields onFieldChange={onFieldChange} />
      <Hr />
      <ExtractionFields />
      <Hr />
      <Translation />
      <DocDocumentInfoFormFamilyField onFieldChange={onFieldChange} />
      <Hr />
    </div>
  );
}
