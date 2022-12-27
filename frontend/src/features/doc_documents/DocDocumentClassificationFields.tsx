import { Form, Select, DatePicker, Switch, Input, Tooltip } from 'antd';
import { languageCodes } from '../retrieved_documents/types';
import { prettyDate } from '../../common';
import { DocumentTypes } from '../retrieved_documents/types';
import { DocCompareToPrevious } from './lineage/DocCompareToPrevious';
import { useGetDocDocumentQuery } from './docDocumentApi';
import { ExploreLineage } from './lineage/ExploreLineage';
import { Link, useParams } from 'react-router-dom';
import { useCallback, useState } from 'react';
import { useSelector } from 'react-redux';
import {
  lineageDocDocumentTableState,
  setLineageDocDocumentTableFilter,
  setPreviousDocDocumentId,
} from './lineage/lineageDocDocumentsSlice';
import { useAppDispatch } from '../../app/store';
import { QuestionCircleOutlined } from '@ant-design/icons';

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

const HasPrevious = ({ setModalOpen }: { setModalOpen: (open: boolean) => void }) => {
  const form = Form.useFormInstance();
  const previousDocDocId = Form.useWatch('previous_doc_doc_id');

  const handleChange = (hasPrevious: boolean) => {
    if (hasPrevious) {
      setModalOpen(true);
      return;
    }
    form.setFieldsValue({
      previous_doc_doc_id: null,
    });
  };
  return (
    <Form.Item label="Has Previous" valuePropName="checked">
      <Switch onChange={handleChange} checked={previousDocDocId != null} />
    </Form.Item>
  );
};

const UpdateLaterDocs = () => {
  const previousDocDocumentId = Form.useWatch('previous_doc_doc_id');
  const { docDocumentId: updatingDocDocId } = useParams();
  const { data: updatingDocDoc } = useGetDocDocumentQuery(updatingDocDocId, {
    skip: !updatingDocDocId,
  });

  return (
    <Form.Item
      label={
        <Tooltip placement="top" title="Apply change to all later documents in this lineage">
          Update Later Docs
          <QuestionCircleOutlined className="ml-1" />
        </Tooltip>
      }
      name="include_later_documents_in_lineage_update"
      valuePropName="checked"
      className="mb-0 ml-10"
      initialValue={true}
      hidden={
        previousDocDocumentId === updatingDocDoc?.previous_doc_doc_id ||
        updatingDocDoc?.is_current_version
      }
    >
      <Switch />
    </Form.Item>
  );
};

const PrevDoc = () => {
  const previousDocDocId: string | undefined = Form.useWatch('previous_doc_doc_id');
  const { data: prevDoc } = useGetDocDocumentQuery(previousDocDocId, { skip: !previousDocDocId });

  return (
    <>
      {previousDocDocId ? (
        <Link target="_blank" to={`/documents/${prevDoc?._id}`}>
          {prevDoc?.name}
        </Link>
      ) : null}
    </>
  );
};

const Lineage = () => {
  const dispatch = useAppDispatch();
  const [modalOpen, setModalOpen] = useState(false);
  const { docDocumentId: updatingDocDocId } = useParams();
  const { data: updatingDocDoc } = useGetDocDocumentQuery(updatingDocDocId, {
    skip: !updatingDocDocId,
  });
  const prevDocDocId = Form.useWatch('previous_doc_doc_id');
  const form = Form.useFormInstance();
  const tableState = useSelector(lineageDocDocumentTableState);

  const handleModalOpen = useCallback(() => {
    dispatch(setPreviousDocDocumentId(updatingDocDoc?.previous_doc_doc_id));

    const docType = form.getFieldValue('document_type');
    const newFilters = tableState.filter.map((f) => {
      return f.name === 'document_type' ? { ...f, value: docType } : f;
    });
    dispatch(setLineageDocDocumentTableFilter(newFilters));

    setModalOpen(true);
  }, [dispatch, form, updatingDocDoc?.previous_doc_doc_id]);

  const closeModal = useCallback(() => {
    setModalOpen(false);
  }, [setModalOpen]);

  return (
    <>
      <HasPrevious setModalOpen={handleModalOpen} />
      <UpdateLaterDocs />
      <Form.Item label="Lineage" hidden={!prevDocDocId}>
        <PrevDoc />
      </Form.Item>
      <Form.Item hidden name="previous_doc_doc_id">
        <Input />
      </Form.Item>
      <Form.Item noStyle hidden={!prevDocDocId}>
        <ExploreLineage
          open={modalOpen}
          closeModal={closeModal}
          handleModalOpen={handleModalOpen}
        />
      </Form.Item>
    </>
  );
};

export function DocumentClassification() {
  const { docDocumentId } = useParams();
  const { data: docDocument } = useGetDocDocumentQuery(docDocumentId, { skip: !docDocumentId });
  const previousDocDocId: string | undefined = Form.useWatch('previous_doc_doc_id');
  const { data: prevDoc } = useGetDocDocumentQuery(previousDocDocId, { skip: !previousDocDocId });
  const prevDocDocId = Form.useWatch('previous_doc_doc_id');

  return (
    <>
      <div className="flex space-x-8">
        <Form.Item label="Internal" valuePropName="checked" name="internal_document">
          <Switch />
        </Form.Item>
        <Form.Item name="lang_code" label="Language" className="flex-1">
          <Select options={languageCodes} />
        </Form.Item>
        <DocumentType />
        <FinalEffectiveDate />
      </div>

      <div className="flex space-x-8">
        <Lineage />
        {prevDocDocId ? (
          <DocCompareToPrevious
            previousChecksum={prevDoc?.checksum}
            currentChecksum={docDocument?.checksum}
          />
        ) : null}
      </div>
    </>
  );
}
