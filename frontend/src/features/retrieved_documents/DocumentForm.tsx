import { Button, Form, Select, Space, Input, DatePicker } from 'antd';
import { useForm } from 'antd/lib/form/Form';
import moment from 'moment';
import React, { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { prettyDate } from '../../common';
import { useUpdateDocumentMutation } from './documentsApi';
import { RetrievedDocument, DocumentTypes, LanguageCodes } from './types';
const { TextArea } = Input;

export function DocumentForm(props: { doc: RetrievedDocument }) {
  const navigate = useNavigate();
  const params = useParams();
  const [updateDoc] = useUpdateDocumentMutation();
  const [form] = useForm();
  const doc = props.doc;

  const [docTypeConfidence, setDocTypeConfidence] = useState(doc.doc_type_confidence);

  function setFormState(modified: Partial<RetrievedDocument>) {
    if (modified.document_type !== undefined) {
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

  function convertDate(date?: string) {
    if (date) return moment(date);
    return undefined;
  }

  const initialValues = {
    name: doc.name,
    document_type: doc.document_type,
    url: doc.url,
    base_url: doc.base_url,
    lang_code: doc.lang_code,
    link_text: doc.context_metadata?.link_text,
    effective_date: convertDate(doc.effective_date),
    first_collected_date: convertDate(doc.first_collected_date),
    last_collected_date: convertDate(doc.last_collected_date),
    end_date: convertDate(doc.end_date),
    last_updated_date: convertDate(doc.last_updated_date),
    last_reviewed_date: convertDate(doc.last_reviewed_date),
    next_review_date: convertDate(doc.next_review_date),
    next_update_date: convertDate(doc.next_update_date),
    published_date: convertDate(doc.published_date),
  };

  const confidencePercent = docTypeConfidence ? `${Math.floor(docTypeConfidence * 100)}%` : '-';

  const dateFields = [
    {
      name: 'effective_date',
      label: 'Effective Date',
    },
    { name: 'end_date', label: 'End Date' },
    {
      name: 'last_updated_date',
      label: 'Last Updated Date',
    },
    {
      name: 'last_reviewed_date',
      label: 'Last Reviewed Date',
    },
    {
      name: 'next_review_date',
      label: 'Next Review Date',
    },
    {
      name: 'next_update_date',
      label: 'Next Update Date',
    },
    {
      name: 'published_date',
      label: 'Published Date',
    },
    {
      name: 'first_collected_date',
      label: 'First Collected Date',
    },
    {
      name: 'last_collected_date',
      label: 'Last Collected Date',
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
      <Form.Item name="name" label="Name">
        <Input />
      </Form.Item>

      <div className="flex space-x-2">
        <Form.Item className="grow" name="document_type" label="Document Type">
          <Select options={DocumentTypes} />
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
        <Select options={LanguageCodes} />
      </Form.Item>
      <Form.Item name="base_url" label="Base URL">
        <Input disabled />
      </Form.Item>
      <div className="flex space-x-2">
        <Form.Item name="link_text" label="Link Text">
          <TextArea disabled autoSize={true} />
        </Form.Item>
        <Form.Item className="grow" name="url" label="Link URL">
          <TextArea disabled autoSize={true} />
        </Form.Item>
      </div>

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
