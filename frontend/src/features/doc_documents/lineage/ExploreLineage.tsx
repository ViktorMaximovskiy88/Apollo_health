import { Button, Checkbox, Input, Modal } from 'antd';
import { useParams } from 'react-router-dom';
import useLineageSlice from '../../lineage/use-lineage-slice';
import { FileTypeViewer } from '../../retrieved_documents/RetrievedDocumentViewer';
import { debounce } from 'lodash';
import { LineageDocRow } from './LineageDocRow';
import classNames from 'classnames';
import { useState } from 'react';
import { useGetDocDocumentQuery } from '../docDocumentApi';

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
        open={open}
        width="100%"
        bodyStyle={{ height: 'calc(100vh - 70px)' }}
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
          <div className="flex flex-col w-64 mr-2">
            <div className="bg-white mb-1">
              <Input.Search
                allowClear={true}
                placeholder="Search"
                onChange={debounce((e) => {
                  actions.onSearch(e.target.value);
                }, 250)}
              />
            </div>

            <div className="overflow-auto h-full bg-white border-slate-200 border-solid border">
              {displayItems.map((group) => (
                <div key={group.lineageId} className="p-2 mb-1 border">
                  <div
                    className={classNames('text-slate-500 uppercase mb-1 cursor-pointer')}
                    onClick={() => {
                      actions.toggleCollapsed(group);
                    }}
                  >
                    {group.lineageId} ({group.items.length})
                  </div>
                  {!group.collapsed &&
                    group.items.map((item) => (
                      <LineageDocRow
                        key={item._id}
                        doc={item}
                        isSelected={item._id === rightSideDoc?._id || item._id === leftSideDoc?._id}
                        {...actions}
                      />
                    ))}
                </div>
              ))}
            </div>

            <div className="p-1">
              {displayItems.length} groups, {domainItems.length} docs
            </div>
          </div>

          {showCurrentDocument ? (
            <div className="flex flex-1">
              <div className="w-1/2 h-full overflow-auto">
                <div>Previous Document</div>
                <FileTypeViewer
                  doc={currentDocDocument}
                  docId={currentDocDocument?.retrieved_document_id}
                />
              </div>
              <div className="w-1/2 h-full overflow-auto">
                <div>Current Document</div>
                <FileTypeViewer
                  doc={currentDocDocument}
                  docId={currentDocDocument?.retrieved_document_id}
                />
              </div>
            </div>
          ) : (
            <div className="w-full h-full overflow-auto">
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
