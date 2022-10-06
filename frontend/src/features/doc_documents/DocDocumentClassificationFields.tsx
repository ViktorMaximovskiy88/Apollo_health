import { Form, Select, DatePicker, Button } from 'antd';
import { prettyDate } from '../../common';
import { DocumentTypes } from '../retrieved_documents/types';
import { DocCompareToPrevious } from './DocCompareToPrevious';

const DocumentType = () => (
  <Form.Item className="flex-1" name="document_type" label="Document Type" required={true}>
    <Select options={DocumentTypes} />
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

const Explore = () => (
  <div className="flex space-x-8 items-center">
    <Button className="mt-1" onClick={() => alert('Explore clicked')}>
      Explore
    </Button>
  </div>
);

export function DocumentClassification() {
  return (
    <>
      <div className="flex space-x-8">
        <DocumentType />
        <FinalEffectiveDate />
      </div>

      <div className="flex space-x-8">
        <TherapyTagRelevance />
        <Lineage />
        <Explore />
        <DocCompareToPrevious />
      </div>
    </>
  );
}
