import { Form, Select, Button } from 'antd';
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

export function DocumentFamily({ doc }: { doc: DocDocument }) {
  const [options, setOptions] = useState<string[]>([]);

  const [isModalVisible, showModal, closeModal] = useModal();

  return (
    <div className="flex space-x-8">
      <AddDocumentFamily
        closeModal={closeModal}
        visible={isModalVisible}
        doc={doc}
        options={options}
        setOptions={setOptions}
      />
      <Form.Item name="document_family" label="Document Family" className="flex-1">
        <Select mode="multiple" allowClear placeholder="None selected">
          {options.map((documentFamilyName) => (
            <Option key={documentFamilyName}>{documentFamilyName}</Option>
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
