import { Form, Select, Button, FormInstance } from 'antd';
import { DocDocument, DocumentFamilyType, DocumentFamilyOption } from './types';
import { useEffect, useState } from 'react';
import { PlusOutlined } from '@ant-design/icons';
import { AddDocumentFamily } from './DocumentFamilyAddForm';
import { useGetDocumentFamiliesQuery } from './documentFamilyApi';

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

const useOptions = (
  doc: DocDocument
): [DocumentFamilyOption[], (options: DocumentFamilyOption[]) => void] => {
  const { data: documentFamilies } = useGetDocumentFamiliesQuery({
    siteId: doc.site_id,
    documentType: doc.document_type,
  });
  const [options, setOptions] = useState<DocumentFamilyOption[]>([]);

  useEffect(() => {
    if (!documentFamilies) return;

    const initialOptions = documentFamilies.map((df: DocumentFamilyType): DocumentFamilyOption => {
      return {
        ...df,
        label: df.name,
        value: df._id,
      };
    });
    setOptions(initialOptions);
  }, [documentFamilies]);

  return [options, setOptions];
};

export function DocumentFamily({ doc, form }: { doc: DocDocument; form: FormInstance }) {
  const [options, setOptions] = useOptions(doc);
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
