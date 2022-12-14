import { Button, Tooltip } from 'antd';
import { useEffect, useState } from 'react';

import { CompareDocViewer } from './CompareDocumentViewer';
import { FullScreenModal } from '../../../components/FullScreenModal';
import { useLazyGetDiffExistsQuery } from './../docDocumentApi';
import { useTaskWorker } from '../../tasks/taskSlice';
import { CompareResponse } from '../types';

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

export function CompareModal(props: {
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
      {props.newFileKey && props.prevFileKey ? (
        <CompareModalBody newFileKey={props.newFileKey} prevFileKey={props.prevFileKey} />
      ) : (
        <div>Loading...</div>
      )}
    </FullScreenModal>
  );
}

export function DocCompareToPrevious({
  currentChecksum,
  previousChecksum,
}: {
  currentChecksum: string | undefined;
  previousChecksum: string | undefined;
}) {
  const [modalOpen, setModalOpen] = useState(false);
  const [compareResult, setCompareResult] = useState<CompareResponse | undefined>();
  const [getDiffExists] = useLazyGetDiffExistsQuery();

  const enqueueTask = useTaskWorker(() => {
    setModalOpen(true);
    if (compareResult) {
      setCompareResult({ ...compareResult, exists: true, pending: false });
    }
  });

  useEffect(() => {
    async function diffExists() {
      if (currentChecksum && previousChecksum) {
        const result = await getDiffExists({
          current_checksum: currentChecksum,
          previous_checksum: previousChecksum,
        }).unwrap();
        setCompareResult(result);
      }
    }
    diffExists();
  }, [getDiffExists, currentChecksum, previousChecksum]);

  return (
    <div className="flex space-x-8 items-center">
      {currentChecksum && previousChecksum ? (
        <Button
          loading={compareResult?.pending}
          className="mt-1"
          onClick={() => {
            if (compareResult && !compareResult.exists) {
              enqueueTask('PDFDiffTask', {
                current_checksum: currentChecksum,
                previous_checksum: previousChecksum,
              });
              setCompareResult({ ...compareResult, pending: true });
            } else {
              setModalOpen(true);
            }
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
        newFileKey={compareResult?.new_key}
        prevFileKey={compareResult?.prev_key}
        modalOpen={modalOpen}
        handleCloseModal={() => setModalOpen(false)}
      />
    </div>
  );
}
