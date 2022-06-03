import {
  Button,
  Form,
  Select,
  Space,
  Switch,
  Radio,
  Input,
  DatePicker,
} from 'antd';
import type { RadioChangeEvent } from 'antd';
import { useForm } from 'antd/lib/form/Form';
import { format, parse, parseISO } from 'date-fns';
import React, { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useUpdateDocumentMutation } from './documentsApi';
import { RetrievedDocument } from './types';

import moment from 'moment';

export function DocumentForm(props: { doc: RetrievedDocument }) {
  const navigate = useNavigate();
  const params = useParams();
  const [updateDoc] = useUpdateDocumentMutation();
  const [form] = useForm();
  const doc = props.doc;

  const [automatedExtraction, setAutomatedExtraction] = useState(
    doc.automated_content_extraction
  );

  const [effectiveDateSelection, setEffectiveDateSelection] = useState(
    (doc.identified_dates || []).find((date) => date === doc.effective_date)
      ? 'list'
      : 'custom'
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

  function onEffectiveDateSelectionChange(e: RadioChangeEvent) {
    setEffectiveDateSelection(e.target.value);
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
    { value: 'Authorization Policy', label: 'Authorization Policy' },
    { value: 'Provider Guide', label: 'Provider Guide' },
    { value: 'Treatment Request Form', label: 'Treatment Request Form' },
    { value: 'Payer Unlisted Policy', label: 'Payer Unlisted Policy' },
    { value: 'Covered Treatment List', label: 'Covered Treatment List' },
    { value: 'Regulatory Document', label: 'Regulatory Document' },
    { value: 'Formulary', label: 'Formulary' },
    { value: 'Internal Reference', label: 'Internal Reference' },
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

      <Form.Item name="effective_date" label="Effective Date" preserve>
        <Radio.Group
          className="mb-1"
          onChange={onEffectiveDateSelectionChange}
          defaultValue={effectiveDateSelection}
        >
          <Radio value="list">From List</Radio>
          <Radio value="custom">Custom</Radio>
        </Radio.Group>

        {effectiveDateSelection === 'list' && (
          <Select
            defaultValue={initialValues.effective_date}
            options={dateOptions}
            onChange={(value) => {
              form.setFieldsValue({ effective_date: value });
            }}
          />
        )}

        {effectiveDateSelection === 'custom' && (
          <DatePicker
            className="flex"
            defaultValue={moment(initialValues.effective_date)}
            onChange={(value: any) => {
              form.setFieldsValue({
                effective_date: value.utc().format('YYYY-MM-DD'),
              });
            }}
          />
        )}
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
