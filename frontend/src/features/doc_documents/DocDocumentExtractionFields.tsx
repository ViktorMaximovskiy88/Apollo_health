import { Form, Select } from 'antd';
import { languageCodes } from '../retrieved_documents/types';

export const ExtractionFields = () => {
  return (
    <div className="flex space-x-8">
      <Form.Item name="lang_code" label="Language" className="flex-1">
        <Select options={languageCodes} />
      </Form.Item>
    </div>
  );
};
