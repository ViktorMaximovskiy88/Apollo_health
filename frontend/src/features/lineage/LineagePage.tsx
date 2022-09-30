import classNames from 'classnames';
import { Button, Input, notification } from 'antd';
import { MainLayout } from '../../components';
import { useParams } from 'react-router-dom';
import { useGetSiteLineageQuery, useLazyProcessSiteLineageQuery } from './lineageApi';
import useLineageSlice from './use-lineage-slice';
import { SiteMenu } from '../sites/SiteMenu';
import { FileTypeViewer } from '../retrieved_documents/RetrievedDocumentViewer';
import { TextEllipsis } from '../../components';
import _, { debounce } from 'lodash';
import { prettyDateUTCFromISO } from '../../common/date';

export function LineagePage() {
  const { siteId } = useParams();

  useGetSiteLineageQuery(siteId, {
    pollingInterval: 5000,
  });

  const [processSiteLineage] = useLazyProcessSiteLineageQuery();
  const { state, actions } = useLineageSlice();
  const { list, leftSideDoc, rightSideDoc } = state;

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
          <Input.Search allowClear={true} placeholder="Search" />

          <div className="overflow-auto h-full  bg-white">
            {list.filtered.map((group) => (
              <div key={group.lineageId} className="p-2 mb-4 border">
                <div className="text-slate-500 uppercase mb-2">
                  {group.lineageId} ({group.items.length})
                </div>
                {group.items.map((item) => (
                  <div
                    key={item._id}
                    className={classNames(
                      'p-2 my-2 bg-slate-50 border group relative',
                      item._id == leftSideDoc?._id && ['border-l-2', 'border-gray-100 ']
                    )}
                  >
                    <TextEllipsis text={item.name} />
                    <TextEllipsis text={item.document_type} />
                    <div>{prettyDateUTCFromISO(item.final_effective_date)}</div>
                    <div className="hidden group-hover:block absolute bottom-2 right-2 z-50">
                      <Button
                        onClick={() => {
                          console.log(item, actions.setLeftSide);
                          actions.setLeftSide(item);
                        }}
                      >
                        Left
                      </Button>

                      <Button
                        onClick={() => {
                          actions.setRightSide(item);
                        }}
                      >
                        Right
                      </Button>
                    </div>
                  </div>
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
