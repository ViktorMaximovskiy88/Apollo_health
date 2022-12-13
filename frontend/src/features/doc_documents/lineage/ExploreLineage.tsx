import { Button, Checkbox, Form } from 'antd';
import { useParams } from 'react-router-dom';
import { FileTypeViewer } from '../../retrieved_documents/RetrievedDocumentViewer';
import { useCallback, useState } from 'react';
import { useGetDocDocumentQuery } from '../docDocumentApi';
import { LineageDocDocumentsTable } from './LineageDocDocumentsTable';
import { useSelector } from 'react-redux';
import { previousDocDocumentIdState, setPreviousDocDocumentId } from './lineageDocDocumentsSlice';
import { useAppDispatch } from '../../../app/store';
import { DocDocument } from '../types';
import { FullScreenModal } from '../../../components/FullScreenModal';

const LineageDocViewer = ({ doc, label }: { doc?: DocDocument; label: string }) => {
  return (
    <div className="mr-2 flex-grow flex flex-col">
      <h3>{label}</h3>
      <div className="overflow-auto">
        <FileTypeViewer doc={doc} docId={doc?.retrieved_document_id} />
      </div>
    </div>
  );
};

const LineageModalBody = ({ showCurrentDocument }: { showCurrentDocument: boolean }) => {
  const { docDocumentId } = useParams();
  const { data: currentDocDocument } = useGetDocDocumentQuery(docDocumentId);

  const previousDocDocumentId = useSelector(previousDocDocumentIdState);
  const { data: previousDocDocument } = useGetDocDocumentQuery(previousDocDocumentId ?? '');

  return (
    <div className="flex flex-row h-full">
      <div className="flex-grow flex flex-col mr-2 z-10">
        <h3>Documents</h3>
        <LineageDocDocumentsTable />
      </div>
      <LineageDocViewer label="Previous Document" doc={previousDocDocument} />
      {showCurrentDocument ? (
        <LineageDocViewer label="Current Document" doc={currentDocDocument} />
      ) : null}
    </div>
  );
};

const LineageModalFooter = (props: {
  showCurrentDocument: boolean;
  setShowCurrentDocument: (showCurrentDocument: boolean) => void;
  handleCancel: () => void;
  handleSubmit: () => Promise<void>;
}) => {
  const previousDocDocumentId = useSelector(previousDocDocumentIdState);
  return (
    <div className="flex">
      <div className="mr-auto">
        <Checkbox
          checked={props.showCurrentDocument}
          onChange={(e) => props.setShowCurrentDocument(e.target.checked)}
        >
          Show Current Document
        </Checkbox>
      </div>
      <div>
        <Button key="cancel" onClick={props.handleCancel}>
          Cancel
        </Button>
        <Button
          key="submit"
          type="primary"
          onClick={props.handleSubmit}
          disabled={!previousDocDocumentId}
        >
          Submit
        </Button>
      </div>
    </div>
  );
};

export function ExploreLineage() {
  const form = Form.useFormInstance();

  const { docDocumentId: updatingDocDocId } = useParams();
  const { data: updatingDocDoc } = useGetDocDocumentQuery(updatingDocDocId, {
    skip: !updatingDocDocId,
  });

  const dispatch = useAppDispatch();
  const prevDocDocId = useSelector(previousDocDocumentIdState);
  const [open, setOpen] = useState(false);
  const [showCurrentDocument, setShowCurrentDocument] = useState(true);

  const closeModal = useCallback(() => {
    setOpen(false);
  }, []);

  const handleCancel = useCallback(() => {
    dispatch(setPreviousDocDocumentId(null));
    closeModal();
  }, [closeModal, dispatch]);

  const handleModalOpen = useCallback(() => {
    dispatch(setPreviousDocDocumentId(updatingDocDoc?.previous_doc_doc_id));
    setOpen(true);
  }, [dispatch, prevDocDocId, updatingDocDoc?.previous_doc_doc_id]);

  const handleSubmit = useCallback(async () => {
    if (!prevDocDocId) throw new Error('prevDocDocId not found');
    form.setFieldValue('previous_doc_doc_id', prevDocDocId);
    closeModal();
  }, [prevDocDocId, form, closeModal]);

  return (
    <div className="flex space-x-8 items-center">
      <Button className="mt-1" onClick={handleModalOpen}>
        Explore
      </Button>

      <FullScreenModal
        title="Explore Lineage"
        open={open}
        onCancel={handleCancel}
        footer={[
          <LineageModalFooter
            showCurrentDocument={showCurrentDocument}
            setShowCurrentDocument={setShowCurrentDocument}
            handleCancel={handleCancel}
            handleSubmit={handleSubmit}
          />,
        ]}
      >
        <LineageModalBody showCurrentDocument={showCurrentDocument} />
      </FullScreenModal>
    </div>
  );
}
