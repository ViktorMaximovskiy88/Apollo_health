import { Form, Select } from 'antd';
import { DocumentFamilyType, DocumentFamilyOption } from './types';
import { createContext, useEffect, useState } from 'react';
import { useGetDocumentFamiliesQuery } from './documentFamilyApi';
import { useParams } from 'react-router-dom';
import { useGetDocDocumentQuery } from './docDocumentApi';
import { FormInstance, Rule } from 'antd/lib/form';
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
      form.resetFields(['document_families']);
    } else {
      form.setFieldsValue({ document_families: [] });
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
    setOptions(newOptions);
  }, [documentFamilies]);

  return [options, setOptions];
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
      if (selections.length <= 1) return Promise.resolve();
      const selectedDocumentFamilies = documentFamilies.filter((df) => selections.includes(df._id));
      const [firstDocumentFamily] = selectedDocumentFamilies;

      for (const df of selectedDocumentFamilies) {
        if (df.document_type_threshold !== firstDocumentFamily.document_type_threshold) {
          return Promise.reject(
            `Document Type Confidence Thresholds are different.
            Document Family "${df.name}" has a threshold of ${df.document_type_threshold}%,
            and Document Family "${firstDocumentFamily.name}" has a threshold of
            ${firstDocumentFamily.document_type_threshold}%.`
          );
        }
        if (df.therapy_tag_status_threshold !== firstDocumentFamily.therapy_tag_status_threshold) {
          return Promise.reject(
            `Therapy Tag Status Confidence Thresholds are different.
            Document Family "${df.name}" has a threshold of ${df.therapy_tag_status_threshold}%,
            and Document Family "${firstDocumentFamily.name}" has a threshold of
            ${firstDocumentFamily.therapy_tag_status_threshold}%.`
          );
        }
        if (df.lineage_threshold !== firstDocumentFamily.lineage_threshold) {
          return Promise.reject(
            `Lineage Confidence Thresholds are different.
            Document Family "${df.name}" has a threshold of ${df.lineage_threshold}%,
            and Document Family "${firstDocumentFamily.name}" has a threshold of
            ${firstDocumentFamily.lineage_threshold}%.`
          );
        }
      }
      return Promise.resolve();
    },
  });
  return mustMatchThresholds;
};

export const DocDocumentFormContext = createContext<FormInstance>({} as FormInstance);

export function DocumentFamily() {
  useSyncedValue();
  const [options, setOptions] = useSyncedOptions();
  const mustMatchThresholds = useMustMatchThresholds();

  return (
    <div className="flex space-x-8">
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
      <AddNewDocumentFamilyButton options={options} setOptions={setOptions} />
    </div>
  );
}
