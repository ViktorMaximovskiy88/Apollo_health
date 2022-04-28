import { Button, Form, Select, Space, Switch } from 'antd';
import { Input } from 'antd';
import { useForm } from 'antd/lib/form/Form';
import { format, parse, parseISO } from 'date-fns';
import { FieldData } from 'rc-field-form/lib/interface';
import React, { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useGetDocumentQuery, useUpdateDocumentMutation } from './documentsApi';
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

  function checkAutomatedExtraction(modified: Partial<RetrievedDocument>) {
    if (modified.automated_content_extraction !== undefined) {
      setAutomatedExtraction(modified.automated_content_extraction);
    }
  }

  function onCancel(e: React.SyntheticEvent) {
    e.preventDefault();
    navigate(-1);
  }
  async function onFinish(doc: Partial<RetrievedDocument>) {
    await updateDoc({
      ...doc,
      effective_date: parse(
        doc.effective_date || '',
        'yyyy-MM-dd',
        0
      ).toISOString(),
      _id: params.docId,
    });
    navigate(-1);
  }

  const initialValues = {
    name: doc.name,
    effective_date: doc.effective_date
      ? format(parseISO(doc.effective_date), 'yyyy-MM-dd')
      : null,
    document_type: doc.document_type,
    automated_content_extraction: doc.automated_content_extraction,
    automated_content_extraction_class: doc.automated_content_extraction_class,
    url: doc.url,
  };

  const documentTypes = [
    { value: 'PA', label: 'Prior Authorization' },
    { value: 'ST', label: 'Step Therapy' },
    { value: 'Formulary', label: 'Formulary' },
  ];

  const extractionOptions = [
    { value: 'BasicTableExtraction', label: 'Basic Table Extraction' },
    { value: 'UHCFormularyExtraction', label: 'UHC Formulary Extraction' },
  ];

  const dateOptions =
    doc.identified_dates?.map((d) => {
      const date = format(parseISO(d), 'yyyy-MM-dd');
      return { value: date, label: date };
    }) || [];
  const today = format(new Date(), 'yyyy-MM-dd');
  dateOptions.push({value: today, label: today });

  return (
    <Form
      layout="vertical"
      form={form}
      requiredMark={false}
      initialValues={initialValues}
      onFinish={onFinish}
      onValuesChange={checkAutomatedExtraction}
    >
      <Form.Item name="name" label="Name">
        <Input />
      </Form.Item>
      <Form.Item name="document_type" label="Document Type">
        <Select options={documentTypes} />
      </Form.Item>
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
