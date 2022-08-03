import { useState } from 'react';
import { Form, Select, Switch, Input, DatePicker, FormInstance } from 'antd';
import { ListDatePicker, Hr } from '../../components';
import { DocCompare } from './DocCompare';
import { prettyDate } from '../../common';
import { DocDocument } from './types';

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

interface DateFieldPropTypes {
  form: FormInstance;
  doc: DocDocument;
  onFieldChange: Function;
}

const Name = () => (
  <Form.Item name="name" label="Name" required={true}>
    <Input />
  </Form.Item>
);
const DocumentType = () => (
  <Form.Item className="flex-1" name="document_type" label="Document Type" required={true}>
    <Select options={documentTypes} />
  </Form.Item>
);
const FinalEffectiveDate = () => (
  <Form.Item name="final_effective_date" label="Final Effective Date" className="flex-1">
    <DatePicker
      className="flex flex-1"
      disabled
      placeholder=""
      format={(value) => prettyDate(value.toDate())}
    />
  </Form.Item>
);
const TherapyTagRelevance = () => (
  <Form.Item className="flex-1" label="Therapy Tag Relevance" required={true}>
    <Select options={[]} />
  </Form.Item>
);
const Lineage = () => (
  <Form.Item label="Lineage" className="flex-1">
    <Select options={[]} />
  </Form.Item>
);
const EffectiveDate = ({ form, doc, onFieldChange }: DateFieldPropTypes) => (
  <ListDatePicker
    form={form}
    className="flex-1"
    name="effective_date"
    defaultValue={doc.effective_date}
    label={'Effective Date'}
    dateList={doc.identified_dates}
    onChange={onFieldChange}
  />
);
const EndDate = ({ form, doc, onFieldChange }: DateFieldPropTypes) => (
  <ListDatePicker
    form={form}
    className="flex-1"
    name="end_date"
    defaultValue={doc.end_date}
    label={'End Date'}
    dateList={doc.identified_dates}
    onChange={onFieldChange}
  />
);
const LastUpdatedDate = ({ form, doc, onFieldChange }: DateFieldPropTypes) => (
  <ListDatePicker
    form={form}
    className="flex-1"
    name="last_updated_date"
    defaultValue={doc.last_updated_date}
    label={'Last Updated Date'}
    dateList={doc.identified_dates}
    onChange={onFieldChange}
  />
);
const LastReviewedDate = ({ form, doc, onFieldChange }: DateFieldPropTypes) => (
  <ListDatePicker
    form={form}
    className="flex-1"
    name="last_reviewed_date"
    defaultValue={doc.last_reviewed_date}
    label={'Last Reviewed Date'}
    dateList={doc.identified_dates}
    onChange={onFieldChange}
  />
);
const NextReviewedDate = ({ form, doc, onFieldChange }: DateFieldPropTypes) => (
  <ListDatePicker
    form={form}
    className="flex-1"
    name="next_review_date"
    defaultValue={doc.next_review_date}
    label={'Next Review Date'}
    dateList={doc.identified_dates}
    onChange={onFieldChange}
  />
);
const NextUpdateDate = ({ form, doc, onFieldChange }: DateFieldPropTypes) => (
  <ListDatePicker
    form={form}
    className="flex-1"
    name="next_update_date"
    defaultValue={doc.next_update_date}
    label={'Next Update Date'}
    dateList={doc.identified_dates}
    onChange={onFieldChange}
  />
);
const PublishedDate = ({ form, doc, onFieldChange }: DateFieldPropTypes) => (
  <ListDatePicker
    form={form}
    className="flex-1"
    name="published_date"
    defaultValue={doc.published_date}
    label={'Published Date'}
    dateList={doc.identified_dates}
    onChange={onFieldChange}
  />
);
const FirstCollectedDate = ({ form, doc, onFieldChange }: DateFieldPropTypes) => (
  <ListDatePicker
    form={form}
    disabled={true}
    className="flex-1"
    name="first_collected_date"
    defaultValue={doc.first_collected_date}
    label={'First Collected Date'}
    dateList={doc.identified_dates}
    onChange={onFieldChange}
  />
);
const LastCollectedDate = ({ form, doc, onFieldChange }: DateFieldPropTypes) => (
  <ListDatePicker
    form={form}
    disabled={true}
    className="flex-1"
    name="last_collected_date"
    defaultValue={doc.last_collected_date}
    label={'Last Collected Date'}
    dateList={doc.identified_dates}
    onChange={onFieldChange}
  />
);
const Language = () => (
  <Form.Item name="lang_code" label="Language" className="flex-1">
    <Select options={languageCodes} />
  </Form.Item>
);
const AutomatedContentExtraction = ({
  setAutomatedExtraction,
}: {
  setAutomatedExtraction: (automatedExtraction: any) => void;
}) => (
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
);
const ExtractionStrategy = () => (
  <Form.Item name="automated_content_extraction_class" label="Extraction Strategy">
    <Select options={extractionOptions} />
  </Form.Item>
);
const BaseUrl = ({ doc }: { doc: DocDocument }) => (
  <Form.Item name="base_url" label="Base URL">
    {doc.base_url && (
      <a target="_blank" href={doc.base_url} rel="noreferrer">
        {doc.base_url}
      </a>
    )}
  </Form.Item>
);
const LinkText = ({ doc }: { doc: DocDocument }) => (
  <Form.Item name="link_text" label="Link Text">
    {doc.link_text}
  </Form.Item>
);
const LinkUrl = ({ doc }: { doc: DocDocument }) => (
  <Form.Item className="grow" name="url" label="Link URL">
    {doc.url && (
      <a target="_blank" href={doc.url} rel="noreferrer">
        {doc.url}
      </a>
    )}
  </Form.Item>
);

export function DocDocumentInfoForm(props: {
  doc: DocDocument;
  form: FormInstance;
  onFieldChange: Function;
}) {
  const { doc, form, onFieldChange } = props;

  const [automatedExtraction, setAutomatedExtraction] = useState(doc.automated_content_extraction);

  return (
    <>
      <Name />
      <Hr />

      <div className="flex space-x-8">
        <DocumentType />
        <FinalEffectiveDate />
      </div>

      <div className="flex space-x-8">
        <TherapyTagRelevance />
        <Lineage />
      </div>

      <DocCompare org_doc={doc} />
      <Hr />

      <div className="flex flex-1 space-x-8">
        <EffectiveDate form={form} doc={doc} onFieldChange={onFieldChange} />
        <EndDate form={form} doc={doc} onFieldChange={onFieldChange} />
        <LastUpdatedDate form={form} doc={doc} onFieldChange={onFieldChange} />
      </div>

      <div className="flex flex-1 space-x-8">
        <LastReviewedDate form={form} doc={doc} onFieldChange={onFieldChange} />
        <NextReviewedDate form={form} doc={doc} onFieldChange={onFieldChange} />
        <NextUpdateDate form={form} doc={doc} onFieldChange={onFieldChange} />
      </div>

      <div className="flex flex-1 space-x-8">
        <PublishedDate form={form} doc={doc} onFieldChange={onFieldChange} />
        <FirstCollectedDate form={form} doc={doc} onFieldChange={onFieldChange} />
        <LastCollectedDate form={form} doc={doc} onFieldChange={onFieldChange} />
      </div>

      <Hr />

      <div className="flex space-x-8">
        <Language />
        <AutomatedContentExtraction setAutomatedExtraction={setAutomatedExtraction} />
      </div>

      {automatedExtraction && <ExtractionStrategy />}

      <Hr />

      <BaseUrl doc={doc} />
      <LinkText doc={doc} />
      <LinkUrl doc={doc} />
    </>
  );
}
