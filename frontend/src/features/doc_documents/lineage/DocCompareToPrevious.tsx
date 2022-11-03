import { Button, Form, notification, Tooltip } from 'antd';
import { useCallback, useState } from 'react';

import { CompareDocViewer } from './CompareDocumentViewer';
import { isErrorWithData } from '../../../common/helpers';
import { FullScreenModal } from '../../../components/FullScreenModal';
import { useCreateDiffMutation, useGetDocDocumentQuery } from './../docDocumentApi';

function CompareModalBody(props: { newFileKey?: string; prevFileKey?: string }) {
  return (
    <div className="flex h-full">
      <div className="mr-2 flex-grow flex flex-col">
        <h3>Previous Document</h3>
        <div className="overflow-auto">
          <CompareDocViewer fileKey={props.prevFileKey} />
        </div>
      </div>
      <div className="mr-2 flex-grow flex flex-col">
        <h3>Current Document</h3>
        <div className="overflow-auto">
          <CompareDocViewer fileKey={props.newFileKey} />
        </div>
      </div>
    </div>
  );
}

function CompareModal(props: {
  newFileKey?: string;
  prevFileKey?: string;
  modalOpen: boolean;
  handleCloseModal: (e: React.MouseEvent<HTMLElement, MouseEvent>) => void;
}) {
  return (
    <FullScreenModal
      title="Previous Document Compare"
      footer={null}
      open={props.modalOpen}
      onCancel={props.handleCloseModal}
    >
      <CompareModalBody newFileKey={props.newFileKey} prevFileKey={props.prevFileKey} />
    </FullScreenModal>
  );
}

export function DocCompareToPrevious() {
  const form = Form.useFormInstance();
  const currentDocDocId: string = form.getFieldValue('docId');
  const { data: currentDocument } = useGetDocDocumentQuery(currentDocDocId);
  const [modalOpen, setModalOpen] = useState(false);
  const [newKey, setNewKey] = useState<string>();
  const [prevKey, setPrevKey] = useState<string>();
  const [createDiff, { isLoading, isSuccess }] = useCreateDiffMutation();

  const { previous_doc_doc_id: previousDocDocId } = currentDocument ?? {};

  function handleCloseModal() {
    setModalOpen(false);
  }
  const handleCompare = useCallback(async () => {
    if (!previousDocDocId) throw new Error('DocDocument has no Previous DocDoc Id');
    try {
      const diffRes = await createDiff({ currentDocDocId, previousDocDocId }).unwrap();
      if (diffRes.queued) {
        notification.success({
          message: 'Generating Comparison Files',
          description: 'The comparison files have been queued for creation.',
        });
      } else if (diffRes.processing) {
        notification.info({
          message: 'Generating Comparison Files',
          description: 'The comparison files are being created.',
        });
      } else if (diffRes.exists && diffRes.new_key && diffRes.prev_key) {
        setNewKey(diffRes.new_key);
        setPrevKey(diffRes.prev_key);
        setModalOpen(true);
      } else {
        throw new Error('Invalid Response');
      }
    } catch (err) {
      if (isErrorWithData(err)) {
        notification.error({
          message: 'Error Creating Compare File',
          description: `${err.data.detail}`,
        });
      } else {
        notification.error({
          message: 'Error Creating Compare File',
          description: JSON.stringify(err),
        });
      }
    }
  }, [createDiff, currentDocDocId, previousDocDocId]);

  return (
    <div className="flex space-x-8 items-center">
      {previousDocDocId ? (
        <Button className="mt-1" loading={isLoading} onClick={handleCompare} type="primary">
          Compare To Previous
        </Button>
      ) : (
        <Tooltip title={'No previous document ID. Comparison is not possible.'}>
          <Button className="mt-1" type="primary" disabled={true}>
            Compare To Previous
          </Button>
        </Tooltip>
      )}
      <CompareModal
        newFileKey={newKey}
        prevFileKey={prevKey}
        modalOpen={modalOpen}
        handleCloseModal={handleCloseModal}
      />
    </div>
  );
}
