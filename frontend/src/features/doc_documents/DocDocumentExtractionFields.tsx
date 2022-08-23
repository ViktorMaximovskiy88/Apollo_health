import { Form, Select } from 'antd';
import { LanguageCodes } from '../retrieved_documents/types';

const Language = () => (
  <Form.Item name="lang_code" label="Language" className="flex-1">
    <Select options={LanguageCodes} />
  </Form.Item>
);

export const ExtractionFields = () => {
  return (
    <>
      <div className="flex space-x-8">
        <Language />
      </div>
    </>
  );
};
