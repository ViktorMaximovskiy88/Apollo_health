import { Form, Select } from 'antd';
import { DocumentFamilyType, DocumentFamilyOption } from './types';
import { createContext, useEffect, useState } from 'react';
import { useGetDocumentFamiliesQuery } from './documentFamilyApi';
import { useParams } from 'react-router-dom';
import { useGetDocDocumentQuery } from './docDocumentApi';
import { FormInstance } from 'antd/lib/form';
import { AddNewDocumentFamilyButton } from './DocumentFamilyAddNew';

const { Option } = Select;

const useSyncedValue = () => {
  const { docDocumentId: docId } = useParams();
  const { data: doc } = useGetDocDocumentQuery(docId);
  const form = Form.useFormInstance();
  const documentType = Form.useWatch('document_type', form);

  useEffect(() => {
    if (!doc) return;

    if (documentType === doc.document_type) {
      form.resetFields(['document_family']);
    } else {
      form.setFieldsValue({ document_family: null });
    }
  }, [doc, documentType, form]);
};

const useSyncedOptions = (): [
  DocumentFamilyOption[],
  (options: DocumentFamilyOption[]) => void
] => {
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
    setOptions([{ label: 'None', value: null }, ...newOptions]);
  }, [documentFamilies]);

  return [options, setOptions];
};

export const DocDocumentFormContext = createContext<FormInstance>({} as FormInstance);

export function DocumentFamily() {
  useSyncedValue();
  const [options, setOptions] = useSyncedOptions();

  return (
    <div className="flex space-x-8">
      <Form.Item name="document_family" label="Document Family" className="flex-1">
        <Select allowClear placeholder="Options loading...">
          {options.map(({ label, value }) => (
            <Option key={value} value={value}>
              {label}
            </Option>
          ))}
        </Select>
      </Form.Item>
      <AddNewDocumentFamilyButton options={options} setOptions={setOptions} />
    </div>
  );
}
