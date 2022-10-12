import { Button, Checkbox, Input, Modal } from 'antd';
import { useParams } from 'react-router-dom';
import useLineageSlice from '../../lineage/use-lineage-slice';
import { FileTypeViewer } from '../../retrieved_documents/RetrievedDocumentViewer';
import { debounce } from 'lodash';
import { LineageDocRow } from './LineageDocRow';
import classNames from 'classnames';
import { useState } from 'react';
import { useGetDocDocumentQuery } from '../docDocumentApi';
import { LineageDocDocumentsTable } from './LineageDocDocumentsTable';

export function ExploreLineage() {
  const { docDocumentId } = useParams();
  const { data: currentDocDocument } = useGetDocDocumentQuery(docDocumentId);

  const { state, actions } = useLineageSlice();
  const { displayItems, domainItems, leftSideDoc, rightSideDoc } = state;
  const [open, setOpen] = useState(false);
  const [showCurrentDocument, setShowCurrentDocument] = useState(true);

  return (
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
          <Checkbox
            className="mr-[85%]"
            checked={showCurrentDocument}
            onChange={(e) => setShowCurrentDocument(e.target.checked)}
          >
            Show Current Document
          </Checkbox>,
          <Button key="cancel" onClick={() => setOpen(false)}>
            Cancel
          </Button>,
          <Button
            key="submit"
            type="primary"
            onClick={() => alert('TODO: update previous document id')}
          >
            Submit
          </Button>,
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
              <div className="w-1/2 h-full">
                Previous Document
                <FileTypeViewer
                  doc={currentDocDocument}
                  docId={currentDocDocument?.retrieved_document_id}
                />
              </div>
              <div className="w-1/2 h-full">
                Current Document
                <FileTypeViewer
                  doc={currentDocDocument}
                  docId={currentDocDocument?.retrieved_document_id}
                />
              </div>
            </div>
          ) : (
            <div className="w-1/2 h-full">
              <div>Previous Document</div>
              <FileTypeViewer
                doc={currentDocDocument}
                docId={currentDocDocument?.retrieved_document_id}
              />
            </div>
          )}
        </div>
      </Modal>
    </div>
  );
}
