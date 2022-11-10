import { Form, Select, DatePicker, Switch, Input } from 'antd';
import { languageCodes } from '../retrieved_documents/types';
import { prettyDate } from '../../common';
import { DocumentTypes } from '../retrieved_documents/types';
import { DocCompareToPrevious } from './lineage/DocCompareToPrevious';
import { useGetDocDocumentQuery } from './docDocumentApi';
import { ExploreLineage } from './lineage/ExploreLineage';
import { Link, useParams } from 'react-router-dom';
import { useEffect } from 'react';

const DocumentType = () => (
  <Form.Item className="flex-1" name="document_type" label="Document Type" required={true}>
    <Select showSearch options={DocumentTypes} />
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
  const form = Form.useFormInstance();

  const { docDocumentId } = useParams();
  const { data: docDocument } = useGetDocDocumentQuery(docDocumentId, { skip: !docDocumentId });
  const previousDocDocId: string | undefined = Form.useWatch('previous_doc_doc_id');
  const { data: prevDoc } = useGetDocDocumentQuery(previousDocDocId, { skip: !docDocumentId });

  useEffect(() => {
    form.setFieldValue('previous_doc_doc_id', docDocument?.previous_doc_doc_id);
  }, [docDocument?.previous_doc_doc_id, form]);

  return (
    <>
      <Form.Item label="Lineage" className="flex-1">
        {previousDocDocId ? <Link to={`../${prevDoc?._id}`}>{prevDoc?.name}</Link> : null}
      </Form.Item>
      <Form.Item hidden name="previous_doc_doc_id">
        <Input />
      </Form.Item>
      <Form.Item noStyle>
        <ExploreLineage />
      </Form.Item>
    </>
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

        <DocCompareToPrevious />
      </div>
    </>
  );
}
