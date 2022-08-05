import { useState } from 'react';
import { Form, Select, Switch, Input, DatePicker } from 'antd';
import { ListDatePicker, Hr } from '../../components';
import { DocCompare } from './DocCompare';
import { prettyDate } from '../../common';
import { DocDocument } from './types';
import { DocumentTypes, LanguageCodes } from "../retrieved_documents/types"

export function DocDocumentInfoForm(props: {
  doc: DocDocument;
  form: any;
  onFieldChange: Function;
}) {
  const { doc, form, onFieldChange } = props;

  const [automatedExtraction, setAutomatedExtraction] = useState(doc.automated_content_extraction);

  const extractionOptions = [
    { value: 'BasicTableExtraction', label: 'Basic Table Extraction' },
    { value: 'UHCFormularyExtraction', label: 'UHC Formulary Extraction' },
    { value: 'MedigoldFormularyExtraction', label: 'Medigold Formulary Extraction' },
  ];

  return (
    <>
      <Form.Item name="name" label="Name" required={true}>
        <Input />
      </Form.Item>

      <Hr />

      <div className="flex space-x-8">
        <Form.Item className="flex-1" name="document_type" label="Document Type" required={true}>
          <Select options={DocumentTypes} />
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

      <DocCompare org_doc={doc} />

      <Hr />

      <div className="flex flex-1 space-x-8">
        <ListDatePicker
          form={form}
          className="flex-1"
          name="effective_date"
          defaultValue={doc.effective_date}
          label={'Effective Date'}
          dateList={doc.identified_dates}
          onChange={onFieldChange}
        />

        <ListDatePicker
          form={form}
          className="flex-1"
          name="end_date"
          defaultValue={doc.end_date}
          label={'End Date'}
          dateList={doc.identified_dates}
          onChange={onFieldChange}
        />

        <ListDatePicker
          form={form}
          className="flex-1"
          name="last_updated_date"
          defaultValue={doc.last_updated_date}
          label={'Last Updated Date'}
          dateList={doc.identified_dates}
          onChange={onFieldChange}
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
          onChange={onFieldChange}
        />

        <ListDatePicker
          form={form}
          className="flex-1"
          name="next_review_date"
          defaultValue={doc.next_review_date}
          label={'Next Review Date'}
          dateList={doc.identified_dates}
          onChange={onFieldChange}
        />

        <ListDatePicker
          form={form}
          className="flex-1"
          name="next_update_date"
          defaultValue={doc.next_update_date}
          label={'Next Update Date'}
          dateList={doc.identified_dates}
          onChange={onFieldChange}
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
          onChange={onFieldChange}
        />

        <ListDatePicker
          form={form}
          className="flex-1"
          name="first_collected_date"
          defaultValue={doc.first_collected_date}
          label={'First Collected Date'}
          dateList={doc.identified_dates}
          onChange={onFieldChange}
        />
        <ListDatePicker
          form={form}
          className="flex-1"
          name="last_collected_date"
          defaultValue={doc.last_collected_date}
          label={'Last Collected Date'}
          dateList={doc.identified_dates}
          onChange={onFieldChange}
        />
      </div>

      <Hr />

      <div className="flex space-x-8">
        <Form.Item name="lang_code" label="Language" className="flex-1">
          <Select options={LanguageCodes} />
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
        {doc.base_url && (
          <a target="_blank" href={doc.base_url}>
            {doc.base_url}
          </a>
        )}
      </Form.Item>

      <Form.Item name="link_text" label="Link Text">
        {doc.link_text}
      </Form.Item>

      <Form.Item className="grow" name="url" label="Link URL">
        {doc.url && (
          <a target="_blank" href={doc.url}>
            {doc.url}
          </a>
        )}
      </Form.Item>
    </>
  );
}
