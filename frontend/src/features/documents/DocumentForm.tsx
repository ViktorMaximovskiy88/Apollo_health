import { Button, Form, Select, Space, Switch } from 'antd';
import { Input } from 'antd';
import { useForm } from 'antd/lib/form/Form';
import { prettyDate, toIsoDateUtc } from '../../common';
import React, { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useUpdateDocumentMutation } from './documentsApi';
import { RetrievedDocument } from './types';

export function DocumentForm(props: { doc: RetrievedDocument }) {
  const navigate = useNavigate();
  const params = useParams();
  const [updateDoc] = useUpdateDocumentMutation();
  const [form] = useForm();
  const doc = props.doc;
  const [automatedExtraction, setAutomatedExtraction] = useState(
    doc.automated_content_extraction
  );
  const [docTypeConfidence, setDocTypeConfidence] = useState(
    doc.doc_type_confidence
  );

  function setFormState(modified: Partial<RetrievedDocument>) {
    if (modified.automated_content_extraction !== undefined) {
      setAutomatedExtraction(modified.automated_content_extraction);
    } else if (modified.document_type !== undefined) {
      if (modified.document_type === doc.document_type) {
        setDocTypeConfidence(doc.doc_type_confidence);
      } else {
        setDocTypeConfidence(undefined);
      }
    }
  }

  function onCancel(e: React.SyntheticEvent) {
    e.preventDefault();
    navigate(-1);
  }

  async function onFinish(doc: Partial<RetrievedDocument>) {
    await updateDoc({
      ...doc,
      _id: params.docId,
    });
    navigate(-1);
  }

  const initialValues = {
    name: doc.name,
    effective_date: doc.effective_date,
    document_type: doc.document_type,
    automated_content_extraction: doc.automated_content_extraction,
    automated_content_extraction_class: doc.automated_content_extraction_class,
    url: doc.url,
    base_url: doc.base_url,
  };

  const documentTypes = [
    { value: 'Authorization Policy', label: 'Authorization Policy' },
    { value: 'Provider Guide', label: 'Provider Guide' },
    { value: 'Treatment Request Form', label: 'Treatment Request Form' },
    { value: 'Payer Unlisted Policy', label: 'Payer Unlisted Policy' },
    { value: 'Covered Treatment List', label: 'Covered Treatment List' },
    { value: 'Regulatory Document', label: 'Regulatory Document' },
    { value: 'Formulary', label: 'Formulary' },
    { value: 'Internal Reference', label: 'Internal Reference' },
  ];

  const confidencePercent = docTypeConfidence
    ? `${Math.floor(docTypeConfidence * 100)}%`
    : '-';

  const extractionOptions = [
    { value: 'BasicTableExtraction', label: 'Basic Table Extraction' },
    { value: 'UHCFormularyExtraction', label: 'UHC Formulary Extraction' },
  ];

  const dateOptions =
    doc.identified_dates?.map((d) => {
      return { value: d, label: prettyDate(d) };
    }) || [];

  const today = prettyDate(new Date().toISOString());
  dateOptions.push({ value: toIsoDateUtc(today), label: today });

  return (
    <Form
      layout="vertical"
      form={form}
      requiredMark={false}
      initialValues={initialValues}
      onFinish={onFinish}
      onValuesChange={setFormState}
    >
      <Form.Item name="name" label="Name">
        <Input />
      </Form.Item>
      <div className="flex space-x-2">
        <Form.Item className="grow" name="document_type" label="Document Type">
          <Select options={documentTypes} />
        </Form.Item>
        <Form.Item label="Confidence">
          <div className="flex justify-center">{confidencePercent}</div>
        </Form.Item>
      </div>
      <Form.Item name="effective_date" label="Effective Date">
        <Select options={dateOptions} />
      </Form.Item>
      <Form.Item
        name="automated_content_extraction"
        label="Automated Content Extraction"
        valuePropName="checked"
      >
        <Switch />
      </Form.Item>
      {automatedExtraction && (
        <Form.Item
          name="automated_content_extraction_class"
          label="Extraction Strategy"
        >
          <Select options={extractionOptions} />
        </Form.Item>
      )}
      <Form.Item name="base_url" label="Base URL">
        <Input disabled />
      </Form.Item>
      <Form.Item name="url" label="URL">
        <Input disabled />
      </Form.Item>

      <Form.Item>
        <Space>
          <Button type="primary" htmlType="submit">
            Submit
          </Button>
          <Button htmlType="submit" onClick={onCancel}>
            Cancel
          </Button>
        </Space>
      </Form.Item>
    </Form>
  );
}
