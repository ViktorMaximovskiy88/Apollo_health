import { Form, Select, DatePicker, Switch, Input } from 'antd';
import { languageCodes } from '../retrieved_documents/types';
import { prettyDate } from '../../common';
import { DocumentTypes } from '../retrieved_documents/types';
import { ExploreLineage } from './lineage/ExploreLineage';
import { DocCompareToPrevious } from './DocCompareToPrevious';
import { useGetDocDocumentQuery, useUpdatePrevDocDocMutation } from './docDocumentApi';
import { useParams } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';

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
  const [updatePreviousDocDocument] = useUpdatePrevDocDocMutation();

  const { docId } = useParams();
  const { data: doc } = useGetDocDocumentQuery(docId, { skip: !docId });

  const [previousDocDocId, setPreviousDocDocumentId] = useState(doc?.previous_doc_doc_id ?? '');
  useEffect(() => {
    setPreviousDocDocumentId(doc?.previous_doc_doc_id ?? '');
  }, [doc]);

  const { data: prevDoc } = useGetDocDocumentQuery(previousDocDocId, { skip: !previousDocDocId });

  const onUpdatePreviousDocDocument = async (newPrevDocDocId: string) => {
    if (!docId) return;
    setPreviousDocDocumentId(newPrevDocDocId);
    await updatePreviousDocDocument({ updatingDocDocId: docId, prevDocDocId: previousDocDocId });
  };

  return (
    <>
      <Form.Item label="Lineage" className="flex-1">
        <Link to={`../${prevDoc?._id}`}>{prevDoc?.name}</Link>
      </Form.Item>
      <Form.Item name="previous_doc_doc_id" noStyle>
        <Input hidden value={previousDocDocId} />
        <ExploreLineage onChange={onUpdatePreviousDocDocument} value={previousDocDocId} />
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
