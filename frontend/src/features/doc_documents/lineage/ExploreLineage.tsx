import { Button, Checkbox } from 'antd';
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
  const { data: docDocument } = useGetDocDocumentQuery(previousDocDocumentId);

  return (
    <div className="flex flex-row h-full">
      <div className="flex-grow flex flex-col mr-2">
        <h3>Documents</h3>
        <LineageDocDocumentsTable />
      </div>
      <LineageDocViewer label="Previous Document" doc={docDocument} />
      {showCurrentDocument ? (
        <LineageDocViewer label="Current Document" doc={currentDocDocument} />
      ) : null}
    </div>
  );
};

export function ExploreLineage(props: {
  onChange?: (previousDocDocumentId: string) => void;
  value?: string;
}) {
  const dispatch = useAppDispatch();
  const previousDocDocumentId = useSelector(previousDocDocumentIdState);
  const [open, setOpen] = useState(false);
  const [showCurrentDocument, setShowCurrentDocument] = useState(true);

  const closeModal = useCallback(() => setOpen(false), [setOpen]);

  const handleModalOpen = useCallback(() => {
    if (props.value) {
      dispatch(setPreviousDocDocumentId(props.value));
    }
    setOpen(true);
  }, [dispatch, setOpen, props]);

  const handleSubmit = useCallback(() => {
    props.onChange?.(previousDocDocumentId);
    closeModal();
  }, [props, previousDocDocumentId, closeModal]);

  return (
    <div className="flex space-x-8 items-center">
      <Button className="mt-1" onClick={handleModalOpen}>
        Explore
      </Button>

      <FullScreenModal
        title="Explore Lineage"
        open={open}
        onCancel={closeModal}
        footer={[
          <div className="flex">
            <div className="mr-auto">
              <Checkbox
                checked={showCurrentDocument}
                onChange={(e) => setShowCurrentDocument(e.target.checked)}
              >
                Show Current Document
              </Checkbox>
            </div>
            <div>
              <Button key="cancel" onClick={closeModal}>
                Cancel
              </Button>
              <Button key="submit" type="primary" onClick={handleSubmit}>
                Submit
              </Button>
            </div>
          </div>,
        ]}
      >
        <LineageModalBody showCurrentDocument={showCurrentDocument} />
      </FullScreenModal>
    </div>
  );
}
