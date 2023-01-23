import ReactDataGrid from '@inovua/reactdatagrid-community';
import { Button, notification, Spin } from 'antd';
import { useCallback, useMemo, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import {
  useDataTableFilter,
  useDataTablePagination,
  useDataTableSort,
  useInterval,
} from '../../common/hooks';
import { DocDocument } from '../doc_documents/types';
import { useGetWorkQueueQuery } from './workQueuesApi';
import { MainLayout } from '../../components';
import { useGetSitesQuery } from '../sites/sitesApi';
import {
  workQueueTableState,
  setWorkQueueTableFilter,
  setWorkQueueTableSort,
  setWorkQueueTableLimit,
  setWorkQueueTableSkip,
} from './workQueueSlice';
import { useSelector } from 'react-redux';
import {
  useLazyGetWorkQueueItemsQuery,
  useTakeNextWorkItemMutation,
} from '../doc_documents/docDocumentApi';
import { useWorkQueueColumns } from './useWorkQueueColumns';

function useGetSiteNamesById() {
  const [siteIds, setSiteIds] = useState<string[]>([]);
  const { data: sites } = useGetSitesQuery(
    {
      filterValue: [{ name: '_id', operator: 'eq', type: 'string', value: siteIds }],
    },
    { skip: siteIds.length === 0 }
  );
  const siteNamesById = useMemo(() => {
    const map: { [key: string]: string } = {};
    sites?.data.forEach((site) => {
      map[site._id] = site.name;
    });
    return map;
  }, [sites]);
  return { setSiteIds, siteNamesById };
}

function uniqueSiteIds(items: DocDocument[]) {
  const usedSiteIds: { [key: string]: boolean } = {};
  items.forEach((item) => item.locations.forEach((l) => (usedSiteIds[l.site_id] = true)));
  return Object.keys(usedSiteIds);
}

export function WorkQueuePage() {
  const queueId = useParams().queueId;
  const navigate = useNavigate();
  const [getWorkItemFn, { isFetching }] = useLazyGetWorkQueueItemsQuery();
  const { data: wq } = useGetWorkQueueQuery(queueId);
  const [takeNextWorkItem] = useTakeNextWorkItemMutation();

  const tableState = useSelector(workQueueTableState);
  const takeNext = useCallback(async () => {
    const response = await takeNextWorkItem({ queueId, tableState });
    if ('data' in response) {
      if (!response.data.acquired_lock) {
        notification.success({
          message: 'Queue Empty',
          description: 'Congratulations! This queue has been emptied.',
        });
      } else {
        navigate(`../${response.data.item_id}/process`);
      }
    }
  }, [takeNextWorkItem, navigate, queueId, tableState]);

  const { isActive, setActive, watermark } = useInterval(10000);
  const { setSiteIds, siteNamesById } = useGetSiteNamesById();
  const { columns } = useWorkQueueColumns(queueId, siteNamesById, wq);

  const loadData = useCallback(
    async (tableInfo: any) => {
      const { data } = await getWorkItemFn({ ...tableInfo, id: queueId });
      const items = data?.data ?? [];
      const count = data?.total ?? 0;
      if (items) setSiteIds(uniqueSiteIds(items));
      return { data: items, count };
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [getWorkItemFn, queueId, watermark]
  );

  const filterProps = useDataTableFilter(workQueueTableState, setWorkQueueTableFilter);
  const sortProps = useDataTableSort(workQueueTableState, setWorkQueueTableSort);
  const paginationProps = useDataTablePagination(
    workQueueTableState,
    setWorkQueueTableLimit,
    setWorkQueueTableSkip,
    { isActive, setActive }
  );

  if (!wq) return null;
  return (
    <MainLayout
      sectionToolbar={
        <>
          <Spin spinning={isFetching} />
          <Button onClick={takeNext}>Take Next</Button>
        </>
      }
    >
      <ReactDataGrid
        dataSource={loadData}
        columns={columns}
        rowHeight={50}
        renderLoadMask={() => <></>}
        {...filterProps}
        {...sortProps}
        {...paginationProps}
        columnUserSelect
      />
    </MainLayout>
  );
}
