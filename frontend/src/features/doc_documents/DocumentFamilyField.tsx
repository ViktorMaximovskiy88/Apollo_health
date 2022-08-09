import { Form, Select, Button } from 'antd';
import { DocumentFamilyType, DocumentFamilyOption } from './types';
import { useEffect, useState } from 'react';
import { PlusOutlined } from '@ant-design/icons';
import { AddDocumentFamily as AddDocumentFamilyModal } from './DocumentFamilyAddForm';
import { useGetDocumentFamiliesQuery } from './documentFamilyApi';
import { useParams } from 'react-router-dom';
import { useGetDocDocumentQuery } from './docDocumentApi';
import { Rule } from 'antd/lib/form';

const { Option } = Select;

const useSyncedValue = () => {
  const { docDocumentId: docId } = useParams();
  const { data: doc } = useGetDocDocumentQuery(docId);
  const form = Form.useFormInstance();
  const documentType = Form.useWatch('document_type', form);

  useEffect(() => {
    if (!doc) return;

    if (documentType === doc.document_type) {
      form.resetFields(['document_families']);
    } else {
      form.setFieldsValue({ document_families: [] });
    }
  }, [doc, documentType, form]);
};

const useSyncedOptions = (): [DocumentFamilyOption[]] => {
  const form = Form.useFormInstance();

  const { docDocumentId: docId } = useParams();
  const { data: doc } = useGetDocDocumentQuery(docId);

  const documentType = Form.useWatch('document_type', form);
  const { data: documentFamilies } = useGetDocumentFamiliesQuery({
    siteId: doc?.site_id ?? '',
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

const useMustMatchThresholds = () => {
  const form = Form.useFormInstance();

  const { docDocumentId: docId } = useParams();
  const { data: doc } = useGetDocDocumentQuery(docId);

  const documentType = Form.useWatch('document_type', form);

  const { data: documentFamilies } = useGetDocumentFamiliesQuery({
    siteId: doc?.site_id ?? '',
    documentType,
  });

  const mustMatchThresholds = () => ({
    async validator(_: Rule, selections: string[]) {
      if (!documentFamilies) return;
      if (selections.length === 0) return Promise.resolve();
      const selectedDocumentFamilies = documentFamilies.filter((df) => df._id in selections);
      const [firstDocumentFamily] = selectedDocumentFamilies;
      for (const df of selectedDocumentFamilies) {
        if (df.document_type_threshold !== firstDocumentFamily.document_type_threshold) {
          return Promise.reject(`Document Type Thresholds different ${''}`);
        }
        if (false) {
          // therapy tag
        }
        if (false) {
          // lineage
        }
      }
      return Promise.resolve();
    },
  });
  return mustMatchThresholds;
};

export function DocumentFamily() {
  useSyncedValue();
  const [options] = useSyncedOptions();
  const [isModalVisible, showModal, closeModal] = useModal();
  const mustMatchThresholds = useMustMatchThresholds();

  return (
    <div className="flex space-x-8">
      <AddDocumentFamilyModal closeModal={closeModal} visible={isModalVisible} />
      <Form.Item
        name="document_families"
        label="Document Family"
        className="flex-1"
        rules={[mustMatchThresholds]}
      >
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
