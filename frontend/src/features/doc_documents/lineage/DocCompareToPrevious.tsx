import { Button, Form, Tooltip } from 'antd';
import { useState } from 'react';

import { CompareDocViewer } from './CompareDocumentViewer';
import { FullScreenModal } from '../../../components/FullScreenModal';
import { useCreateDiffMutation, useGetDocDocumentQuery } from './../docDocumentApi';
import { useTaskWorker } from '../../../app/taskSlice';

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
  const enqueueTask = useTaskWorker(
    () =>
      createDiff({
        currentDocDocId,
        previousDocDocId,
      }),
    (result: any) => {
      let new_key;
      let prev_key;

      if (result.task) {
        const { payload } = result.task;
        new_key = `${payload.current_checksum}-${payload.previous_checksum}-new.pdf`;
        prev_key = `${payload.current_checksum}-${payload.previous_checksum}-prev.pdf`;
      } else {
        new_key = result.new_key;
        prev_key = result.prev_key;
      }

      setNewKey(new_key);
      setPrevKey(prev_key);
      setModalOpen(true);
    }
  );

  return (
    <div className="flex space-x-8 items-center">
      {previousDocDocId ? (
        <Button
          className="mt-1"
          loading={isLoading}
          onClick={() => {
            enqueueTask();
          }}
          type="primary"
        >
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
        handleCloseModal={() => setModalOpen(false)}
      />
    </div>
  );
}
