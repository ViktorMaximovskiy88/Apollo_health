import { Form, Input } from 'antd';

import { Hr } from '../../components';
import { DateFields } from './DocDocumentDateFields';
import { DocumentClassification } from './DocDocumentClassificationFields';
import { Translation } from './TranslationSelector';
import { DocDocumentDocumentFamilyField } from './DocDocumentDocumentFamilyField';

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
      <DocumentClassification onFieldChange={onFieldChange} />
      <Hr />
      <DateFields onFieldChange={onFieldChange} />
      <Hr />
      <DocDocumentDocumentFamilyField onFieldChange={onFieldChange} />
      <Translation />
      <Hr />
      <Form.Item
        name="previous_par_id"
        label="Previous PAR ID"
        rules={[
          {
            message: 'PAR ID must be a valid GUID (e.g. 412d2222-faed-4ff5-ac07-000000000000)',
            pattern: /^[0-9a-f]{8}-[0-9a-f]{4}-[0-5][0-9a-f]{3}-[089ab][0-9a-f]{3}-[0-9a-f]{12}$/i,
          },
        ]}
      >
        <Input />
      </Form.Item>
    </div>
  );
}
