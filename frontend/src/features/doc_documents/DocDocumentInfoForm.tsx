import { useState } from 'react';
import { Form, Select, Switch, Input, DatePicker } from 'antd';
import { ListDatePicker, Hr } from '../../components';
import { prettyDate } from '../../common';
import { DocDocument } from './types';
const { TextArea } = Input;

export function DocDocumentInfoForm(props: { doc: DocDocument; form: any }) {
  const { doc, form } = props;

  const [automatedExtraction, setAutomatedExtraction] = useState(doc.automated_content_extraction);

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
    <>
      <Form.Item name="name" label="Document ID">
        {doc._id}
      </Form.Item>

      <Form.Item name="name" label="Name" required={true}>
        <Input />
      </Form.Item>

      <Hr />

      <div className="flex space-x-8">
        <Form.Item className="flex-1" name="document_type" label="Document Type" required={true}>
          <Select options={documentTypes} />
        </Form.Item>
        <Form.Item name={'final_effective_date'} label={'Final Effective Date'} className="flex-1">
          <DatePicker
            className="flex flex-1"
            disabled
            placeholder=""
            format={(value) => prettyDate(value.toDate())}
          />
        </Form.Item>
      </div>

      <div className="flex space-x-8">
        <Form.Item className="flex-1" label="Therapy Tag Relevance" required={true}>
          <Select options={[]} />
        </Form.Item>
        <Form.Item label={'Lineage'} className="flex-1">
          <Select options={[]} />
        </Form.Item>
      </div>

      <Hr />

      <div className="flex flex-1 space-x-8">
        <ListDatePicker
          form={form}
          className="flex-1"
          name="effective_date"
          defaultValue={doc.effective_date}
          label={'Effective Date'}
          dateList={doc.identified_dates}
        />

        <ListDatePicker
          form={form}
          className="flex-1"
          name="end_date"
          defaultValue={doc.end_date}
          label={'End Date'}
          dateList={doc.identified_dates}
        />

        <ListDatePicker
          form={form}
          className="flex-1"
          name="last_updated_date"
          defaultValue={doc.last_updated_date}
          label={'Last Updated Date'}
          dateList={doc.identified_dates}
        />
      </div>

      <div className="flex flex-1 space-x-8">
        <ListDatePicker
          form={form}
          className="flex-1"
          name="last_reviewed_date"
          defaultValue={doc.last_reviewed_date}
          label={'Last Reviewed Date'}
          dateList={doc.identified_dates}
        />

        <ListDatePicker
          form={form}
          className="flex-1"
          name="next_review_date"
          defaultValue={doc.next_review_date}
          label={'Next Review Date'}
          dateList={doc.identified_dates}
        />

        <ListDatePicker
          form={form}
          className="flex-1"
          name="next_update_date"
          defaultValue={doc.next_update_date}
          label={'Next Update Date'}
          dateList={doc.identified_dates}
        />
      </div>

      <div className="flex flex-1 space-x-8">
        <ListDatePicker
          form={form}
          className="flex-1"
          name="published_date"
          defaultValue={doc.published_date}
          label={'Published Date'}
          dateList={doc.identified_dates}
        />
        {/* maintains spacing; would love to dictch antd form layout */}
        <div className="grow"></div>
        <div className="grow"></div>
      </div>

      <Hr />

      <div className="flex space-x-8">
        <Form.Item name="lang_code" label="Language" className="flex-1">
          <Select options={languageCodes} />
        </Form.Item>

        <Form.Item
          className="flex-1"
          name="automated_content_extraction"
          label="Automated Content Extraction"
          valuePropName="checked"
        >
          <Switch
            onChange={(checked: boolean) => {
              setAutomatedExtraction(checked);
            }}
          />
        </Form.Item>
      </div>

      {automatedExtraction && (
        <Form.Item name="automated_content_extraction_class" label="Extraction Strategy">
          <Select options={extractionOptions} />
        </Form.Item>
      )}

      <Hr />

      <Form.Item name="base_url" label="Base URL">
        <Input disabled />
      </Form.Item>

      <Form.Item name="link_text" label="Link Text">
        <TextArea disabled autoSize={true} />
      </Form.Item>

      <Form.Item className="grow" name="url" label="Link URL">
        <TextArea disabled autoSize={true} />
      </Form.Item>
    </>
  );
}
