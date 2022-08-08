import { Form, Select, Button } from 'antd';
import { DocDocument, DocumentFamilyType, DocumentFamilyOption } from './types';
import { useEffect, useState } from 'react';
import { PlusOutlined } from '@ant-design/icons';
import { AddDocumentFamily as AddDocumentFamilyModal } from './DocumentFamilyAddForm';
import { useGetDocumentFamiliesQuery } from './documentFamilyApi';

const { Option } = Select;

const useSyncedValue = (doc: DocDocument) => {
  const form = Form.useFormInstance();
  const documentType = Form.useWatch('document_type', form);
  useEffect(() => {
    if (!documentType) return;

    if (documentType === doc.document_type) {
      form.resetFields(['document_families']);
    } else {
      form.setFieldsValue({ document_families: [] });
    }
  }, [doc.document_type, documentType, form]);
};

const useSyncedOptions = (doc: DocDocument): [DocumentFamilyOption[]] => {
  const form = Form.useFormInstance();

  const documentType = Form.useWatch('document_type', form);
  const { data: documentFamilies } = useGetDocumentFamiliesQuery({
    siteId: doc.site_id,
    documentType,
  });

  const [options, setOptions] = useState<DocumentFamilyOption[]>([]);

  useEffect(() => {
    if (!documentFamilies) return;

    const newOptions = documentFamilies.map((df: DocumentFamilyType): DocumentFamilyOption => {
      return {
        label: df.name,
        value: df._id,
      };
    });
    setOptions(newOptions);
  }, [documentFamilies]);

  return [options];
};

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

const useSyncWithOtherFields = (doc: DocDocument): [DocumentFamilyOption[]] => {
  useSyncedValue(doc);
  const [options] = useSyncedOptions(doc);
  return [options];
};

export function DocumentFamily({ doc }: { doc: DocDocument }) {
  const form = Form.useFormInstance();
  const [options] = useSyncWithOtherFields(doc);
  const [isModalVisible, showModal, closeModal] = useModal();

  return (
    <div className="flex space-x-8">
      <AddDocumentFamilyModal
        closeModal={closeModal}
        visible={isModalVisible}
        doc={doc}
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
