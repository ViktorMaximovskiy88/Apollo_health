import { Button, Input, notification } from 'antd';
import { MainLayout } from '../../components';
import { useParams } from 'react-router-dom';
import { useGetSiteLineageQuery, useLazyProcessSiteLineageQuery } from './lineageApi';
import useLineageSlice from './use-lineage-slice';
import { SiteMenu } from '../sites/SiteMenu';
import { FileTypeViewer } from '../retrieved_documents/RetrievedDocumentViewer';
import _, { debounce } from 'lodash';
import { LineageDocRow } from './LineageDocRow';

export function LineagePage() {
  const { siteId } = useParams();

  useGetSiteLineageQuery(siteId, {
    pollingInterval: 5000,
  });

  const [processSiteLineage] = useLazyProcessSiteLineageQuery();
  const { state, actions } = useLineageSlice();
  const { displayItems, leftSideDoc, rightSideDoc } = state;

  const openNotification = () => {
    notification.success({
      message: 'Processing lineage...',
    });
  };

  return (
    <MainLayout
      sidebar={<SiteMenu />}
      sectionToolbar={
        <>
          <Button
            onClick={() => {
              processSiteLineage(siteId);
              openNotification();
            }}
            className="ml-auto"
          >
            Reprocess Lineage
          </Button>
        </>
      }
    >
      <div className="flex flex-row h-full">
        <div className="flex flex-col w-64 mr-2 mb-2">
          <Input.Search
            allowClear={true}
            placeholder="Search"
            onChange={debounce((e) => {
              actions.onSearch(e.target.value);
            }, 250)}
          />

          <div className="overflow-auto h-full bg-white">
            {displayItems.map((group) => (
              <div key={group.lineageId} className="p-2 mb-4 border">
                <div className="text-slate-500 uppercase mb-2">
                  {group.lineageId} ({group.items.length})
                </div>
                {group.items.map((item) => (
                  <LineageDocRow key={item._id} doc={item} isSelected={true} {...actions} />
                ))}
              </div>
            ))}
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
