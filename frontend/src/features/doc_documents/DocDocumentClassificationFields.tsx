import { Form, Select, DatePicker } from 'antd';
import { useCallback } from 'react';
import { prettyDate } from '../../common';
import { DocumentTypes } from '../retrieved_documents/types';
import { DocCompareToPrevious } from './DocCompareToPrevious';
import { ExploreLineage } from './lineage/ExploreLineage';

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

export function DocumentClassification() {
  const form = Form.useFormInstance();
  const previousDocDocumentId = Form.useWatch('previous_doc_doc_id');
  const onFinish = useCallback(
    (previous_doc_doc_id: string) => form.setFieldsValue({ previous_doc_doc_id }),
    [form]
  );
  return (
    <>
      <div className="flex space-x-8">
        <DocumentType />
        <FinalEffectiveDate />
      </div>

      <div className="flex space-x-8">
        <TherapyTagRelevance />
        <Lineage />
        <ExploreLineage onFinish={onFinish} previousDocDocumentId={previousDocDocumentId} />
        <DocCompareToPrevious />
      </div>
    </>
  );
}
