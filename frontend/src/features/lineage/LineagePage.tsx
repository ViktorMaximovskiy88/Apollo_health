import { Button, Input } from 'antd';
import { MainLayout } from '../../components';
import { useParams } from 'react-router-dom';
import { useGetSiteLineageQuery, useProcessSiteLineageMutation } from './lineageApi';
import { useLineageSlice } from './lineage-slice';
import { useTaskWorker } from '../../app/taskSlice';
import { SiteMenu } from '../sites/SiteMenu';
import { FileTypeViewer } from '../retrieved_documents/RetrievedDocumentViewer';
import { debounce } from 'lodash';
import { LineageDocRow } from './LineageDocRow';
import classNames from 'classnames';

export function LineagePage() {
  const { siteId } = useParams();

  const [processSiteLineage] = useProcessSiteLineageMutation();
  const { refetch } = useGetSiteLineageQuery(siteId);

  const { state, actions } = useLineageSlice();
  const { displayItems, domainItems, leftSideDoc, rightSideDoc } = state;
  const enqueueTask = useTaskWorker(
    () => processSiteLineage(siteId),
    () => refetch()
  );

  return (
    <MainLayout
      sidebar={<SiteMenu />}
      sectionToolbar={
        <>
          <Button
            onClick={async () => {
              enqueueTask();
            }}
            className="ml-auto"
          >
            Reprocess Lineage
          </Button>
        </>
      }
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
                      setLeftSide={actions.setLeftSide}
                      setRightSide={actions.setRightSide}
                    />
                  ))}
              </div>
            ))}
          </div>

          <div className="p-1">
            {displayItems.length} groups, {domainItems.length} docs
          </div>
        </div>

        <div className="flex flex-1">
          <div className="w-1/2 h-full overflow-auto">
            <div>{leftSideDoc?.name}</div>
            <FileTypeViewer doc={leftSideDoc} docId={leftSideDoc?._id} />
          </div>
          <div className="w-1/2 h-full overflow-auto">
            <div>{rightSideDoc?.name}</div>
            <FileTypeViewer doc={rightSideDoc} docId={rightSideDoc?._id} />
          </div>
        </div>
      </div>
    </MainLayout>
  );
}
