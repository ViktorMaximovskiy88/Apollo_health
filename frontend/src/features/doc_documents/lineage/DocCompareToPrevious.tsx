import { Button, Tooltip } from 'antd';
import { useEffect, useState } from 'react';

import { CompareModal } from './CompareModal';
import { useLazyGetDiffExistsQuery } from './../docDocumentApi';
import { useTaskWorker } from '../../tasks/taskSlice';
import { Task } from '../../tasks/types';
import { CompareResponse } from '../types';

export function DocCompareToPrevious({
  current_doc_id,
  prev_doc_id,
}: {
  current_doc_id?: string;
  prev_doc_id?: string;
}) {
  const [modalOpen, setModalOpen] = useState(false);
  const [compareResult, setCompareResult] = useState<CompareResponse | undefined>();
  const [getDiffExists] = useLazyGetDiffExistsQuery();

  const enqueueTask = useTaskWorker((data: Task) => {
    setModalOpen(true);
    if (compareResult) {
      setCompareResult({
        ...compareResult,
        exists: true,
        pending: false,
        tag_comparison: data.result?.tag_comparison,
      });
    }
  });

  useEffect(() => {
    async function diffExists() {
      if (current_doc_id && prev_doc_id) {
        const result = await getDiffExists({
          current_id: current_doc_id,
          prev_id: prev_doc_id,
        }).unwrap();
        setCompareResult(result);
      }
    }
    diffExists();
  }, [getDiffExists, current_doc_id, prev_doc_id]);

  const handleProcessCompare = () => {
    enqueueTask('PDFDiffTask', {
      current_doc_id: current_doc_id,
      prev_doc_id: prev_doc_id,
    });
    if (compareResult) {
      setCompareResult({ ...compareResult, pending: true });
    }
    setModalOpen(false);
  };

  return (
    <div className="ml-auto flex space-x-8 items-center">
      {current_doc_id && prev_doc_id ? (
        <Button
          loading={compareResult?.pending}
          className="mt-1"
          onClick={() => {
            if (compareResult && !compareResult.exists) {
              handleProcessCompare();
              setModalOpen(false);
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
        tagComparison={compareResult?.tag_comparison}
        processCompare={handleProcessCompare}
      />
    </div>
  );
}
