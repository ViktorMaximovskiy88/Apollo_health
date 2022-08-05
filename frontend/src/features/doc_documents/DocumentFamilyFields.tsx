import { Form, Select, Button, FormInstance } from 'antd';
import { DocDocument } from './types';
import { useState } from 'react';
import { PlusOutlined } from '@ant-design/icons';
import { AddDocumentFamily } from './AddDocumentFamilyForm';

const { Option } = Select;

const useModal = (): [boolean, () => void, () => void] => {
  const [isVisible, setIsVisible] = useState(false);

  const showModal = () => {
    setIsVisible(true);
  };

  const closeModal = () => {
    setIsVisible(false);
  };

  return [isVisible, showModal, closeModal];
};

export function DocumentFamily({ doc, form }: { doc: DocDocument; form: FormInstance }) {
  const [options, setOptions] = useState<{ label: string; value: string }[]>([]);

  const [isModalVisible, showModal, closeModal] = useModal();

  return (
    <div className="flex space-x-8">
      <AddDocumentFamily
        closeModal={closeModal}
        visible={isModalVisible}
        doc={doc}
        options={options}
        setOptions={setOptions}
        docDocumentForm={form}
      />
      <Form.Item name="document_families" label="Document Family" className="flex-1">
        <Select mode="multiple" allowClear placeholder="None selected">
          {options.map(({ label, value }) => (
            <Option key={value} value={value}>
              {label}
            </Option>
          ))}
        </Select>
      </Form.Item>
      <Button className="flex-1 my-7" type="dashed" onClick={showModal}>
        <PlusOutlined />
        Add New Document Family
      </Button>
    </div>
  );
}
