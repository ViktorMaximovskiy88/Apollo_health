import { Button, Checkbox, Modal } from 'antd';
import { useParams } from 'react-router-dom';
import { FileTypeViewer } from '../../retrieved_documents/RetrievedDocumentViewer';
import classNames from 'classnames';
import { useContext, useState } from 'react';
import { useGetDocDocumentQuery } from '../docDocumentApi';
import { LineageDocDocumentsTable } from './LineageDocDocumentsTable';
import { PreviousDocDocContext, PreviousDocDocProvider } from './PreviousDocDocContext';

const PreviousDocDocument = () => {
  const [previousDocDocumentId] = useContext(PreviousDocDocContext);
  const { data: docDocument } = useGetDocDocumentQuery(previousDocDocumentId);
  return (
    <div className="w-1/2 h-full">
      Previous Document
      <FileTypeViewer doc={docDocument} docId={docDocument?.retrieved_document_id} />
    </div>
  );
};

const CurrentDocDocument = () => {
  const { docDocumentId } = useParams();
  const { data: currentDocDocument } = useGetDocDocumentQuery(docDocumentId);
  return (
    <div className="w-1/2 h-full">
      Current Document
      <FileTypeViewer doc={currentDocDocument} docId={currentDocDocument?.retrieved_document_id} />
    </div>
  );
};

export function ExploreLineage({
  onFinish = () => alert('TODO: save previous DocDocument'),
}: {
  onFinish?: () => void;
}) {
  const [open, setOpen] = useState(false);
  const [showCurrentDocument, setShowCurrentDocument] = useState(true);

  return (
    <PreviousDocDocProvider>
      <div className="flex space-x-8 items-center">
        <Button className="mt-1" onClick={() => setOpen(true)}>
          Explore
        </Button>

        <Modal
          className="inset-y-1"
          title="Explore Lineage"
          open={open}
          width="100%"
          bodyStyle={{ height: 'calc(100vh - 150px)' }}
          onCancel={() => setOpen(false)}
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
                <Button key="cancel" onClick={() => setOpen(false)}>
                  Cancel
                </Button>
                <Button key="submit" type="primary" onClick={() => onFinish()}>
                  Submit
                </Button>
              </div>
            </div>,
          ]}
        >
          <div className="flex flex-row h-full">
            <div
              className={classNames('flex flex-col mr-2', showCurrentDocument ? 'w-1/3' : 'w-1/2')}
            >
              Documents
              <LineageDocDocumentsTable />
            </div>

            {showCurrentDocument ? (
              <div className="flex flex-1">
                <PreviousDocDocument />
                <CurrentDocDocument />
              </div>
            ) : (
              <PreviousDocDocument />
            )}
          </div>
        </Modal>
      </div>
    </PreviousDocDocProvider>
  );
}
