import { Form, Select } from 'antd';
import { DocumentFamilyType, DocumentFamilyOption } from './types';
import { createContext, useEffect, useState } from 'react';
import { useGetDocumentFamiliesQuery, documentFamilyApi } from './documentFamilyApi';
import { useParams } from 'react-router-dom';
import { useGetDocDocumentQuery } from './docDocumentApi';
import { FormInstance } from 'antd/lib/form';
import { AddNewDocumentFamilyButton } from './DocumentFamilyAddNew';

const useSyncValueWithDocumentType = () => {
  const { docDocumentId: docId } = useParams();
  const { data: doc } = useGetDocDocumentQuery(docId);
  const form = Form.useFormInstance();
  const documentType = Form.useWatch('document_type', form);

  useEffect(() => {
    if (!doc) return;

    if (documentType === doc.document_type) {
      form.resetFields(['document_family_id']);
    } else {
      form.setFieldsValue({ document_family_id: null });
    }
  }, [doc, documentType, form]);
};

const useSyncOptionsWithDocumentType = (): [
  DocumentFamilyOption[],
  (options: DocumentFamilyOption[]) => void
] => {
  const form = Form.useFormInstance();

  const { docDocumentId: docId } = useParams();
  const { data: doc } = useGetDocDocumentQuery(docId);

  const documentType = Form.useWatch('document_type', form);
  const { data: documentFamilies } = useGetDocumentFamiliesQuery({
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
  useSyncValueWithDocumentType();
  const [options, setOptions] = useSyncOptionsWithDocumentType();
  return (
    <div className="flex space-x-8">
      <Form.Item name="document_family_id" label="Document Family" className="flex-1">
        <Select allowClear options={options} placeholder="Options loading..." />
      </Form.Item>
      <AddNewDocumentFamilyButton options={options} setOptions={setOptions} />
    </div>
  );
}
