import { Form, Select, DatePicker, Switch } from 'antd';
import { languageCodes } from '../retrieved_documents/types';
import { prettyDate } from '../../common';
import { DocumentTypes } from '../retrieved_documents/types';
import { DocCompareToPrevious } from './DocCompareToPrevious';
import { useGetDocDocumentQuery } from './docDocumentApi';
import { useEffect } from 'react';
import { ExploreLineage } from './lineage/ExploreLineage';
import { Link, useParams } from 'react-router-dom';
import { setPreviousDocDocumentId } from './lineage/lineageDocDocumentsSlice';
import { useAppDispatch } from '../../app/store';

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
  const { docDocumentId } = useParams();
  const { data: docDocument } = useGetDocDocumentQuery(docDocumentId, { skip: !docDocumentId });
  const dispatch = useAppDispatch();

  useEffect(() => {
    // on mount, set initial previousDocDocumentId
    dispatch(setPreviousDocDocumentId(docDocument?.previous_doc_doc_id || null));
  }, [dispatch, docDocument?.previous_doc_doc_id]);

  const { data: prevDoc } = useGetDocDocumentQuery(docDocument?.previous_doc_doc_id ?? '');

  return (
    <>
      <Form.Item label="Lineage" className="flex-1">
        <Link to={`../${prevDoc?._id}`}>{prevDoc?.name}</Link>
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
