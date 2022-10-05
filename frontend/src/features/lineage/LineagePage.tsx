import { Button, Input, Radio, notification } from 'antd';
import { FilterTwoTone, FilterOutlined } from '@ant-design/icons';
import { MainLayout } from '../../components';
import { useParams } from 'react-router-dom';
import { useGetSiteLineageQuery, useLazyProcessSiteLineageQuery } from './lineageApi';
import useLineageSlice from './use-lineage-slice';
import { SiteMenu } from '../sites/SiteMenu';
import { FileTypeViewer } from '../retrieved_documents/RetrievedDocumentViewer';
import _, { debounce } from 'lodash';
import { LineageDocRow } from './LineageDocRow';
import classNames from 'classnames';

export function LineagePage() {
  const { siteId } = useParams();

  useGetSiteLineageQuery(siteId, {
    pollingInterval: 5000,
  });

  const [processSiteLineage] = useLazyProcessSiteLineageQuery();
  const { state, actions } = useLineageSlice();
  const { displayItems, domainItems, leftSideDoc, rightSideDoc, filters } = state;
  const hasFilters = filters.multipleLineage || filters.missingLineage || filters.singularLineage;

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
                      isSelected={item._id == rightSideDoc?._id || item._id == leftSideDoc?._id}
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
