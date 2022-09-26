import { useState, useEffect } from 'react';
import { Button, notification } from 'antd';
import { MainLayout } from '../../components';
import { useParams } from 'react-router-dom';
import { useGetSiteLineageQuery, useLazyProcessSiteLineageQuery } from './lineageApi';
import { SiteMenu } from '../sites/SiteMenu';
import { FileTypeViewer } from '../retrieved_documents/RetrievedDocumentViewer';
import { LineageDoc, LineageGroup } from './types';
import { TextEllipsis } from '../../components';
import _ from 'lodash';

export function LineagePage() {
  const { siteId } = useParams();
  const { data: items = [], status } = useGetSiteLineageQuery(siteId, {
    pollingInterval: 5000,
  });
  const [processSiteLineage] = useLazyProcessSiteLineageQuery();

  const [leftSideDoc, setLeftSide] = useState<LineageDoc>();
  const [rightSideDoc, setRighttSide] = useState<LineageDoc>();
  const [lineageGroups, setLineageGroups] = useState<LineageGroup[]>([]);

  // TODO refactor this is view model stuff... uhh
  useEffect(() => {
    const grouped = _(items)
      .groupBy('lineage_id')
      .map((items, lineageId) => {
        const currentIndex = items.findIndex((item) => item.is_current_version);
        const ordered = items.splice(currentIndex, 1);

        while (items.length > 0) {
          const child = ordered[0];
          const parentIndex = items.findIndex((item) => item._id == child.previous_doc_id);
          const [parent] = items.splice(parentIndex, 1);
          ordered.unshift(parent);
        }

        return {
          lineageId,
          items: ordered,
        } as LineageGroup;
      })
      .value();

    setLineageGroups(grouped);
  }, [items.length]);

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
        <div className="overflow-auto w-64 mr-2">
          {lineageGroups.map((group) => (
            <div key={group.lineageId} className="p-2 my-6 bg-white border">
              <div className="text-slate-500 uppercase mb-2">
                {group.lineageId} ({group.items.length})
              </div>
              {group.items.map((item) => (
                <div key={item._id} className="p-2 my-2 bg-slate-50 border group relative">
                  <TextEllipsis text={item.name} />
                  <div className="hidden group-hover:block absolute right-0 z-50">
                    <Button
                      onClick={() => {
                        setLeftSide(item);
                      }}
                    >
                      Left
                    </Button>

                    <Button
                      onClick={() => {
                        setRighttSide(item);
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

        <div className="flex flex-1">
          <div className="w-1/2 h-full overflow-auto">
            <div>{leftSideDoc?.name}</div>
            <FileTypeViewer doc={leftSideDoc} docId={leftSideDoc?._id} />
          </div>
          <div className="w-1/2 h-full overflow-auto ant-tabs-h-full">
            <div>{rightSideDoc?.name}</div>
            <FileTypeViewer doc={rightSideDoc} docId={rightSideDoc?._id} />
          </div>
        </div>
      </div>
    </MainLayout>
  );
}
