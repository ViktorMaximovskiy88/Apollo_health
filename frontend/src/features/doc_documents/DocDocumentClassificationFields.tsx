import { Form, Select, DatePicker } from 'antd';
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

export function DocumentClassification({ doc }: { doc: DocDocument }) {
  return (
    <>
      <div className="flex space-x-8">
        <DocumentType />
        <FinalEffectiveDate />
      </div>

      <div className="flex space-x-8">
        <TherapyTagRelevance />
        <Lineage />
      </div>

      <DocCompare org_doc={doc} />
    </>
  );
}
