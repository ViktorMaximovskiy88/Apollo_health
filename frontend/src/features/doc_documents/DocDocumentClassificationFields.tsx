import { Form, Select, DatePicker, Switch } from 'antd';
import { languageCodes } from '../retrieved_documents/types';
import { prettyDate } from '../../common';
import { DocumentTypes } from '../retrieved_documents/types';
import { useGetDocDocumentQuery } from './docDocumentApi';
import { ExploreLineage } from './lineage/ExploreLineage';
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

const Lineage = () => {
  const prevDocId = Form.useWatch('previous_doc_doc_id');
  const { data: prevDoc } = useGetDocDocumentQuery(prevDocId, { skip: !prevDocId });
  return (
    <Form.Item label="Lineage" className="flex-1">
      <span>{prevDoc?.name}</span>
    </Form.Item>
  );
};

export function DocumentClassification() {
  return (
    <>
      <div className="flex space-x-8">
        <Form.Item label="Internal" valuePropName="checked" name="internal_document">
          <Switch />
        </Form.Item>
        <DocumentType />
        <FinalEffectiveDate />
      </div>

      <div className="flex space-x-8">
        <Form.Item name="lang_code" label="Language" className="flex-1">
          <Select options={languageCodes} />
        </Form.Item>
        <Lineage />
        <Form.Item name="previous_doc_doc_id" noStyle>
          <ExploreLineage />
        </Form.Item>
        <DocCompareToPrevious />
      </div>
    </>
  );
}
