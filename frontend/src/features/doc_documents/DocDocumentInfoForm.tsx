import { Button, Form, Select, Space, Switch, Input, DatePicker } from 'antd';
import { useForm } from 'antd/lib/form/Form';
import moment from 'moment';
import React, { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { prettyDate } from '../../common';
import { DocDocument } from './types';
import { useUpdateDocDocumentMutation } from './docDocumentApi';
const { TextArea } = Input;

export function DocDocumentInfoForm(props: { doc: DocDocument }) {
  const navigate = useNavigate();
  const params = useParams();
  const [updateDocDocument] = useUpdateDocDocumentMutation();
  const [form] = useForm();
  const doc = props.doc;

  const [automatedExtraction, setAutomatedExtraction] = useState(doc.automated_content_extraction);
  const [docTypeConfidence, setDocTypeConfidence] = useState(doc.doc_type_confidence);

  function setFormState(modified: Partial<DocDocument>) {
    if (modified.automated_content_extraction !== undefined) {
      setAutomatedExtraction(modified.automated_content_extraction);
    } else if (modified.document_type !== undefined) {
      if (modified.document_type === doc.document_type) {
        setDocTypeConfidence(doc.doc_type_confidence);
      } else {
        setDocTypeConfidence(-1);
      }
    }
  }

  function onCancel(e: React.SyntheticEvent) {
    e.preventDefault();
    navigate(-1);
  }

  async function onFinish(doc: Partial<DocDocument>) {
    await updateDocDocument({
      ...doc,
      _id: params.docId,
    });
    navigate(-1);
  }

  function convertDate(date?: string) {
    if (date) return moment(date);
    return undefined;
  }

  const initialValues = {
    name: doc.name,
    document_type: doc.document_type,
    automated_content_extraction: doc.automated_content_extraction,
    automated_content_extraction_class: doc.automated_content_extraction_class,
    url: doc.url,
    base_url: doc.base_url,
    lang_code: doc.lang_code,
    // link_text: doc?.context_metadata?.link_text?,
    effective_date: convertDate(doc.effective_date),
    end_date: convertDate(doc.end_date),
    last_updated_date: convertDate(doc.last_updated_date),
    next_review_date: convertDate(doc.next_review_date),
    next_update_date: convertDate(doc.next_update_date),
    published_date: convertDate(doc.published_date),
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

  const languageCodes = [
    { value: 'en', label: 'English' },
    { value: 'es', label: 'Spanish' },
    { value: 'other', label: 'Other' },
  ];

  const confidencePercent = docTypeConfidence ? `${Math.floor(docTypeConfidence * 100)}%` : '-';

  const extractionOptions = [
    { value: 'BasicTableExtraction', label: 'Basic Table Extraction' },
    { value: 'UHCFormularyExtraction', label: 'UHC Formulary Extraction' },
    { value: 'MedigoldFormularyExtraction', label: 'Medigold Formulary Extraction' },
  ];

  const dateFields = [
    {
      name: 'effective_date',
      label: 'Effective Date',
      value: doc.effective_date,
    },
    { name: 'end_date', label: 'End Date', value: doc.end_date },
    {
      name: 'last_updated_date',
      label: 'Last Updated Date',
      value: doc.last_updated_date,
    },
    {
      name: 'next_review_date',
      label: 'Next Review Date',
      value: doc.next_review_date,
    },
    {
      name: 'next_update_date',
      label: 'Next Update Date',
      value: doc.next_update_date,
    },
    {
      name: 'published_date',
      label: 'Published Date',
      value: doc.published_date,
    },
  ];

  return (
    <Form
      layout="vertical"
      form={form}
      requiredMark={false}
      initialValues={initialValues}
      onFinish={onFinish}
      onValuesChange={setFormState}
    >
      <Form.Item name="name" label="Document ID">
        {doc._id}
      </Form.Item>

      <Form.Item name="name" label="Name" required={true}>
        <Input />
      </Form.Item>

      <div className="flex space-x-2">
        <Form.Item className="grow" name="document_type" label="Document Type" required={true}>
          <Select options={documentTypes} />
        </Form.Item>
        <Form.Item label="Confidence">
          <div className="flex justify-center">{confidencePercent}</div>
        </Form.Item>
      </div>

      <div className="flex flex-wrap gap-x-3">
        {dateFields.map((field, i) => {
          return (
            <Form.Item key={i} name={field.name} label={field.label} style={{ flex: '1 0 32%' }}>
              <DatePicker disabled placeholder="" format={(value) => prettyDate(value.toDate())} />
            </Form.Item>
          );
        })}
      </div>

      <Form.Item name="lang_code" label="Language">
        <Select options={languageCodes} />
      </Form.Item>

      <Form.Item
        name="automated_content_extraction"
        label="Automated Content Extraction"
        valuePropName="checked"
      >
        <Switch />
      </Form.Item>

      {automatedExtraction && (
        <Form.Item name="automated_content_extraction_class" label="Extraction Strategy">
          <Select options={extractionOptions} />
        </Form.Item>
      )}

      <Form.Item name="base_url" label="Base URL">
        <Input disabled />
      </Form.Item>

      <Form.Item name="link_text" label="Link Text">
        <TextArea disabled autoSize={true} />
      </Form.Item>

      <Form.Item className="grow" name="url" label="Link URL">
        <TextArea disabled autoSize={true} />
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
